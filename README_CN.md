# CJK 空格后处理代理- llama-proxy

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个专为**llama.cpp**设计的CJK（中文、日文、韩文）空格后处理代理，自动修复中英文混排时的多余空格问题。

## 🌟 特性

- ✨ **透明代理**：OpenAI API 兼容，无需修改客户端代码
- ⚡ **流式处理**：支持SSE 流式响应，逐块清洗文本
- 🔍 **智能检测**：自动识别CJK↔ASCII 边界并修复空格
- 🛡️ **安全缓冲**：避免内容被错误截断
- 🌐 **多格式支持**：OpenAI + Anthropic API 双兼容

## 🇨🇳 中国/内网用户特别提示

### ⚠️ 重要说明

1. **模型下载需要代理**：HuggingFace 在国内访问较慢，建议使用以下方式之一加速：
   -使用镜像源（HF Mirror）-推荐
   -搭建私有代理服务器
   -从国内镜像站下载GGUF 模型文件

2. **pip 安装依赖需要代理**：使用清华源等镜像加速Python 包安装。

###快速开始-内网环境

####方式一：使用HF Mirror（最简单）

```bash
#克隆项目
git clone <your-repo-url>
cd llama-proxy-for-qwen3.5-9b

#设置镜像源
echo 'HF_ENDPOINT=https://hf-mirror.com' > .env

#启动服务
docker-compose up -d
```

####方式二：配置代理服务器

修改`docker-compose.yaml`中的代理配置：

```yaml
build:
  args:
    - HTTP_PROXY=http://your-proxy-server:8087   #替换为您的代理地址
    - HTTPS_PROXY=http://your-proxy-server:8087
```

####方式三：离线部署（提前下载模型）

```bash
#1.在能访问外网的机器上下载模型
aria2c -x 16 -s 16 -k 1M https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/gemma-4-12b-it-Q4_K_M.gguf

#2.将模型文件复制到目标服务器
scp gemma-4-12b-it-Q4_K_M.gguf user@server:/path/to/models/

#3.在目标服务器上启动（无需代理）
docker-compose up -d
```

###本地运行

####安装依赖（使用国内镜像源加速）

```bash
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
pip install fastapi uvicorn[standard] httpx

#运行代理
python llama_proxy/llama_proxy.py
```

## 🧪 测试示例

```bash
curl http://localhost:58080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5-9b",
    "messages": [{"role": "user", "content": "我使用Python 代码计算"}],
    "stream": true
  }' | head -5
```

## 📖 详细文档

|文件|说明|适用人群|
|------|------|--------|
| [README.md](README.md) |英文介绍文档（主入口）|国际用户|
| [GUIDE.md](GUIDE.md) |详细使用指南（中文）|进阶用户|
| [DEPLOYMENT_CN.md](DEPLOYMENT_CN.md) |内网部署指南（重点推荐🇨🇳）|中国/企业用户|
| [快速下载.md](快速下载.md) | GGUF 模型快速下载链接|所有用户|

## 📄 License

MIT License -详见[LICENSE](LICENSE)

---

**Made with ❤️ for CJK community**
