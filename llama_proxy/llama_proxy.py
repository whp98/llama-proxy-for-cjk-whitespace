"""
llama.cpp CJK 空格后处理代理
透明转发 OpenAI 兼容 API，自动去除中文与数字/英文/符号之间的多余空格

用法：
  pip install fastapi uvicorn httpx
  python llama_proxy.py

默认监听 8081，转发到 localhost:8080
可通过环境变量覆盖：
  UPSTREAM=http://localhost:8080  PROXY_PORT=8081  python llama_proxy.py
"""

import os
import re
import json
import asyncio
import logging
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse

# ── 配置 ────────────────────────────────────────────────────────────────────
UPSTREAM   = os.getenv("UPSTREAM",    "http://localhost:8080")
PROXY_PORT = int(os.getenv("PROXY_PORT", "8081"))
LOG_LEVEL  = os.getenv("LOG_LEVEL",   "INFO")

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("llama-proxy")

# ── 正则 ───────────────────────────────────────────────────────────────────────
CJK   = r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]"
ASCII = r'[0-9a-zA-Z!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~]'

_RE_CJK_THEN_ASCII = re.compile(rf"({CJK})\s+({ASCII})")
_RE_ASCII_THEN_CJK = re.compile(rf"({ASCII})\s+({CJK})")
# 修改：只对 ASCII 结尾 HOLD，纯 CJK 结尾直接放行
_RE_TRAILING_HOLD  = re.compile(rf"({ASCII})\s*$")


def clean(text: str) -> str:
    """全量文本后处理"""
    text = _RE_CJK_THEN_ASCII.sub(r"\1\2", text)
    text = _RE_ASCII_THEN_CJK.sub(r"\1\2", text)
    return text


class StreamFixer:
    """
    流式后处理器：每次 feed 一个 chunk，
    把末尾"可能还没收完"的片段 buffer 住，等下一个 chunk 再决定。
    """
    def __init__(self):
        self._buf = ""
        self._last_out = ""  # 记录上次 flush 出去的最后一个字符
    # 记录上一次输出的最后一个字符，供下一次 feed 判断是否需要剥离开头空格
    def _emit(self, text: str) -> str:
        if text:
            self._last_out = text
        return text
    def feed(self, chunk: str) -> str:
        self._buf += chunk

        # 剥离1：buf 以「空格+CJK」开头，且前一输出是 ASCII → 去掉空格
        self._buf = re.sub(
            r'^\s+(?=[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff])',
            '', self._buf
        )

        # ✨ 剥离2：buf 以「空格+ASCII」开头，且前一输出末尾是 CJK → 去掉空格
        _CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
        if self._last_out and _CJK_RE.search(self._last_out[-1]):
            self._buf = re.sub(r'^\s+(?=[0-9a-zA-Z])', '', self._buf)
        cleaned = clean(self._buf)

        if cleaned != self._buf:
            log.debug("[StreamFixer.feed] CLEANED  buf=%r  chunk=%r  →  %r", self._buf, chunk, cleaned)

        # FORCE FLUSH
        if chunk.endswith('\n') or '`' in chunk:
            self._buf = ""
            return self._emit(cleaned)

        if chunk.strip().isdigit():
            self._buf = ""
            return self._emit(cleaned)

        # trailing space HOLD：空格留着等下一个 chunk
        if self._buf.endswith(' ') or self._buf.endswith('\u3000'):
            last_space = len(cleaned.rstrip(' \u3000'))
            safe = cleaned[:last_space]
            self._buf = cleaned[last_space:]
            log.debug("[StreamFixer.feed] HOLD (trailing space)  chunk=%r  buf=%r", chunk, self._buf)
            return self._emit(safe)

        # 原有 ASCII 尾部 HOLD
        m = _RE_TRAILING_HOLD.search(cleaned)
        if m:
            matched_str = m.group()
            if re.match(r'^[a-zA-Z0-9`\s\*]+$', matched_str):
                self._buf = ""
                return self._emit(cleaned)
            safe = cleaned[: m.start()]
            self._buf = cleaned[m.start():]
            log.debug("[StreamFixer.feed] HOLD     chunk=%r  safe=%r  buf=%r", chunk, safe, self._buf)
            return self._emit(safe)

        self._buf = ""
        return self._emit(cleaned)

    def flush(self) -> str:
        out, self._buf = self._buf, ""
        if out:
            log.debug("[StreamFixer.flush] leftover=%r", out)
        return out

# ── FastAPI ──────────────────────────────────────────────────────────────────
app = FastAPI(title="llama-proxy")
_client = httpx.AsyncClient(base_url=UPSTREAM, timeout=300)


def _upstream_headers(request: Request) -> dict:
    skip = {"host", "content-length", "transfer-encoding"}
    return {k: v for k, v in request.headers.items() if k.lower() not in skip}


def _extract_openai_delta(obj: dict) -> tuple[str, bool]:
    """返回 (content, found)"""
    try:
        delta = obj["choices"][0]["delta"].get("content") or ""
        return delta, True
    except (KeyError, IndexError):
        return "", False


def _extract_anthropic_delta(obj: dict) -> tuple[str, bool]:
    """返回 (content, found)"""
    try:
        if obj.get("type") == "content_block_delta":
            text = obj["delta"].get("text") or ""
            return text, True
    except (KeyError, TypeError):
        pass
    return "", False


async def _stream_sse(response: httpx.Response) -> AsyncIterator[bytes]:
    fixer = StreamFixer()

    async for raw_line in response.aiter_lines():
        line = raw_line
        log.debug("[sse-raw-data]: %r", line)
        # 跳过 event: 行和空行，原样透传
        if not line.startswith("data:"):
            yield (line + "\n").encode()
            continue

        payload = line[5:].strip()

        if payload == "[DONE]":
            leftover = fixer.flush()
            if leftover:
                log.debug("[stream] flush leftover: %r", leftover)
            yield b"data: [DONE]\n\n"
            continue

        # ── 找到下面这段逻辑并进行替换 ──────────────────────────────────────────────
        try:
            obj = json.loads(payload)
        except json.JSONDecodeError:
            yield (line + "\n\n").encode()
            continue
        # ==========================================================
        # # ==========================================
        # 1. 尝试 OpenAI 格式
        delta, found = _extract_openai_delta(obj)
        if found and delta:
            obj["choices"][0]["delta"]["content"] = fixer.feed(delta)
            log.debug("[stream] openai delta: %r", delta)
        else:
            # 2. 尝试 Anthropic 文本格式
            delta, found = _extract_anthropic_delta(obj)
            if found and delta:
                cleaned = fixer.feed(delta)
                obj["delta"]["text"] = cleaned
                log.debug("[stream] anthropic delta: %r → %r", delta, cleaned)
            
            # 【修改此分支】：3. 尝试 Anthropic 工具调用的 partial_json 格式
            elif obj.get("type") == "content_block_delta" and "delta" in obj:
                if "partial_json" in obj["delta"]:
                    raw_json_chunk = obj["delta"]["partial_json"]
                    
                    # 💡 核心修改：如果是 JSON 符号（如结尾是" } \n 等），直接输出，不进入 StreamFixer 的 HOLD 逻辑
                    if re.search(r'[\{\}\"\\\,\n]$', raw_json_chunk):
                        # 把之前 buffer 里积攒的字全部清空刷出，并带上当前 chunk
                        cleaned_json_chunk = fixer.flush() + raw_json_chunk
                    else:
                        # 普通含字文本，才走 StreamFixer 缓冲
                        cleaned_json_chunk = fixer.feed(raw_json_chunk)
                        
                    obj["delta"]["partial_json"] = cleaned_json_chunk
                    log.debug("[stream] anthropic tool delta: %r → %r", raw_json_chunk, cleaned_json_chunk)
            
        yield (f"data: {json.dumps(obj, ensure_ascii=False)}\n\n").encode()

    leftover = fixer.flush()
    if leftover:
        log.debug("[stream] end flush leftover: %r", leftover)


def _process_non_stream(body: bytes, content_type: str) -> bytes:
    if "application/json" not in content_type:
        return body
    try:
        obj = json.loads(body)

        # OpenAI 格式
        for choice in obj.get("choices", []):
            msg = choice.get("message", {})
            if msg.get("content"):
                msg["content"] = clean(msg["content"])

        # Anthropic 格式
        for block in obj.get("content", []):
            if block.get("type") == "text" and block.get("text"):
                original = block["text"]
                block["text"] = clean(original)
                if block["text"] != original:
                    log.debug("[non-stream] anthropic cleaned: %r → %r", original, block["text"])

        return json.dumps(obj, ensure_ascii=False).encode()
    except Exception:
        return body

# ── 通用代理路由 ──────────────────────────────────────────────────────────────
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def proxy(path: str, request: Request):
    body = await request.body()
    headers = _upstream_headers(request)

    # 判断是否为流式请求
    is_stream = False
    if body:
        try:
            req_json = json.loads(body)
            is_stream = bool(req_json.get("stream", False))
        except Exception:
            pass

    url = f"/{path}"
    if request.url.query:
        url += f"?{request.url.query}"

    log.info("%s %s stream=%s", request.method, url, is_stream)

    if is_stream:
        # 流式：用 async_stream 保持连接打开
        upstream_req = _client.build_request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
        )
        upstream_resp = await _client.send(upstream_req, stream=True)

        resp_headers = {
            k: v for k, v in upstream_resp.headers.items()
            if k.lower() not in {"content-length", "transfer-encoding"}
        }
        return StreamingResponse(
            _stream_sse(upstream_resp),
            status_code=upstream_resp.status_code,
            headers=resp_headers,
            media_type="text/event-stream",
        )
    else:
        # 非流式：等待完整响应再处理
        upstream_resp = await _client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
        )
        resp_body = _process_non_stream(
            upstream_resp.content,
            upstream_resp.headers.get("content-type", ""),
        )
        resp_headers = {
            k: v for k, v in upstream_resp.headers.items()
            if k.lower() not in {"content-length", "transfer-encoding"}
        }
        return Response(
            content=resp_body,
            status_code=upstream_resp.status_code,
            headers=resp_headers,
            media_type=upstream_resp.headers.get("content-type", "application/json"),
        )


# ── 启动 ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    log.info("代理启动：localhost:%d → %s", PROXY_PORT, UPSTREAM)
    uvicorn.run(app, host="0.0.0.0", port=PROXY_PORT, log_level=LOG_LEVEL.lower())
