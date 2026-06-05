# llama-proxy for Qwen3.5或其他带空格模型

一个专为**llama.cpp**设计的CJK（中文、日文、韩文）空格后处理代理，解决中英文混排时的多余空格问题。

大大提高claude code或其他agent的路径写入成功率。

## 效果展示

claude code qwen3.5 9b Q4_K_M

```text
❯ 当前目录是啥

● 当前工作目录是：/home/popbob/文档/2026/2605工作/ABC-SDK接入/工作1号文件

✻ Cogitated for 1s

❯ 创建 123.txt 3456.txt 你好.txt

● Write(123.txt)
  ⎿  Wrote 1 lines to 123.txt
      1 (No content)

● Write(3456.txt)
  ⎿  Wrote 1 lines to 3456.txt
      1 (No content)

● Write(你好.txt)
  ⎿  Wrote 1 lines to 你好.txt
      1 (No content)

● 已创建三个空文件：
  - 123.txt
  - 3456.txt
  - 你好.txt

✻ Baked for 7s

❯ 三个文件内容分别是啥

● 这三个文件都是空文件，里面没有任何内容。

  因为之前只是创建了这些文件（使用 Write工具时只指定了文件名和空的content），所以：

  ls -la /home/popbob/文档/2026/2605工作/ABC-SDK接入/工作1号文件/*.txt

  会显示这三个文件的文件大小都是 0字节。

✻ Worked for 3s

❯ ls -la /home/popbob/文档/2026/2605工作/ABC-SDK接入/工作1号文件/*.txt

  Listed 1 directory (ctrl+o to expand)

● 三个文件的大小都是 0字节，说明它们都是空文件：

  ┌──────────┬──────┬────────────┐
  │  文件名  │ 大小 │    权限    │
  ├──────────┼──────┼────────────┤
  │ 123.txt  │ 0 B  │ -rw-rw-r-- │
  ├──────────┼──────┼────────────┤
  │ 3456.txt │ 0 B  │ -rw-rw-r-- │
  ├──────────┼──────┼────────────┤
  │ 你好.txt │ 0 B  │ -rw-rw-r-- │
  └──────────┴──────┴────────────┘

  所有文件都是6月5日10:20创建的，且当前没有任何内容。

✻ Churned for 6s
```



## 📋 项目简介

在使用llm 模型（如Qwen3.5-9B、Gemma 等）进行生成时，当回答中包含中文与英文/数字混合内容时，常会出现不自然的多余空格，例如：

```
❌ 错误输出："我使用python 代码计算结果"
✅ 正确输出："我使用Python代码计算结果"
```

本项目通过在llama.cpp 前端部署一个轻量级代理（FastAPI），对流式响应进行后处理，自动修复CJK 字符与ASCII 字符之间的空格问题。

## ✨ 核心功能

- **透明代理**：OpenAI API 兼容，无需修改客户端代码
- **流式处理**：支持SSE 流式响应，逐块清洗文本
- **智能缓冲**：安全的截断检测机制，避免内容被错误截断
- **多格式支持**：同时支持OpenAI 和Anthropic 格式的响应
- **工具调用优化**：针对JSON partial_json 输出特殊处理

## 🛠️ 技术栈

- Python 3.12+
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [Uvicorn](https://www.uvicorn.org/) - ASGI 服务器
- [HTTPX](https://www.python-httpx.org/) - HTTP 客户端

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

#### 1️⃣ 内网环境配置（中国/企业用户必读）

如果您的网络在中国大陆或企业内网，下载模型时需要代理加速。请先启动内网代理：

```bash
#启动内网代理服务器（使用aria2c 多线程下载）
aria2c -x 16 -s 16 -k 1M https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/gemma-4-12b-it-Q4_K_M.gguf

#或使用内网加速镜像（如阿里云、腾讯云等）
export HF_ENDPOINT=https://hf-mirror.com
```

然后修改`docker-compose.yaml`中的代理配置：

```yaml
args:
  - HTTP_PROXY=http://your-proxy-server:8087   #替换为您的内网代理地址
  - HTTPS_PROXY=http://your-proxy-server:8087
```

#### 2️⃣ 启动服务

```bash
#克隆项目
git clone <repo-url>
cd llama-proxy-for-qwen3.5-9b

#启动服务（包含模型下载）
docker-compose up -d
```

### 方式二：本地运行（内网环境）

#### 基础用法

```bash
#安装依赖
pip install fastapi uvicorn[standard] httpx

#直接运行（默认端口8081）
python llama_proxy/llama_proxy.py

#自定义端口和上游服务
export PROXY_PORT=9000 UPSTREAM=http://localhost:58080
python llama_proxy/llama_proxy.py
```

#### 内网环境配置

如果在中国大陆或企业内网，安装依赖时需要加速：

```bash
#方法1:使用镜像源（推荐）
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
pip install fastapi uvicorn[standard] httpx

#方法2:设置HTTP 代理
export HTTP_PROXY=http://your-proxy-server:8087
export HTTPS_PROXY=http://your-proxy-server:8087
pip install fastapi uvicorn[standard] httpx
```

### 方式三：Docker 单容器

```bash
docker build -t llama-proxy ./llama_proxy
docker run -p 8081:8081 --env UPSTREAM=http://host.docker.internal:58080 \
  --env PROXY_PORT=8081 llama-proxy
```

## 🔧 API 配置

### 环境变量

|变量名|说明|默认值|
|--------|------|--------|
| `UPSTREAM` |上游服务地址| `http://localhost:58080` |
| `PROXY_PORT` |代理监听端口| `8081` |
| `LOG_LEVEL` |日志级别| `INFO` |

### Build Args 代理配置（内网环境）

**说明：** `docker-compose.yaml`中的`build.args`参数用于在Docker 构建时设置网络代理，确保能下载依赖和模型。

```yaml
build:
  args:
    - HTTP_PROXY=http://your-proxy-server:8087   #HTTP 请求代理（如HuggingFace）
    - HTTPS_PROXY=http://your-proxy-server:8087  #HTTPS 请求代理
```

**使用场景：**
- **中国用户**：需要配置代理以访问HuggingFace、PyPI 等国外服务
- **企业内网**：需要通过公司代理服务器下载外部资源
- **离线部署**：可在外网环境预先构建镜像，再分发到内网

### Docker Compose 配置说明

```yaml
services:
  llama-proxy:
    build: ./llama_proxy
    environment:
      - UPSTREAM=http://llama-cpp:58080
      - PROXY_PORT=58080
    ports:
      - "58080:58080"
    depends_on:
      - llama-cpp
```

## 📖 使用示例

### OpenAI API 格式

```bash
curl http://localhost:58080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5-9b",
    "messages": [
      {"role": "user", "content": "如何用Python 计算斐波那契数列？"}
    ],
    "stream": true
  }'
```

### Anthropic API 格式

```bash
curl http://localhost:58080/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5-9b",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "请解释一下机器学习"}
    ]
  }'
```

## 📂 项目结构

```
llama-proxy-for-qwen3.5-9b/
├── README.md                    #英文介绍文档（主入口）
├── README_CN.md                 #中文简介
├── GUIDE.md                     #详细使用指南
├── DEPLOYMENT_CN.md             #内网部署指南（重点推荐🇨🇳）
├── ARCHITECTURE.md              #架构设计文档
├── 快速下载.md                  # GGUF 模型快速下载链接
├── docker-compose.yaml          # Docker Compose 配置
└── llama_proxy/                #代理代码目录
    ├── Dockerfile               # Docker 镜像构建文件
    └── llama_proxy.py          #主程序代码
```

## 🔍 工作原理

1. **请求转发**：客户端请求被代理接收后，透明转发到上游的llama.cpp 服务
2. **流式处理**：对SSE 响应逐块读取，累积缓冲区中的文本
3. **智能清洗**：检测CJK 字符与ASCII 字符之间的空格并修复
4. **安全缓冲**：使用正则表达式判断是否需要截断当前块到缓冲区
5. **响应返回**：将清洗后的内容流式返回给客户端

### 核心算法说明

```python
# CJK → ASCII 空格修复
"中文 " + "英文" → "中文英文"

# ASCII → CJK 空格修复  
"English " + "中文" → "English 中文"
```

## 🧪 测试方法

### 测试脚本示例

```bash
#!/bin/bash
# test-proxy.sh

echo "测试中英文混排..."
curl http://localhost:58080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5-9b",
    "messages": [{"role": "user", "content": "解释什么是Python"}],
    "stream": true
  }' | head -20

echo ""
echo "测试JSON 输出..."
curl http://localhost:58080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5-9b",
    "messages": [{"role": "user", "content": "写一个Python 函数计算平方"}],
    "stream": false
  }' | jq '.'
```

## 📝 开发说明

### 核心类：StreamFixer

负责流式响应的逐块处理，包含以下关键逻辑：

1. **feed(chunk)**:接收SSE chunk，累积到缓冲区并清洗
2. **flush()**:返回剩余缓冲内容（响应结束时调用）
3. **安全放行检查**:识别Markdown、数字等特殊场景，避免误截断

### 核心函数：clean(text)

使用正则表达式批量替换CJK↔ASCII 之间的空格：

```python
# CJK 字符集：基本汉字+扩展A 区
CJK = r"[一-鿿㐀-䶿豈-﫿]"

# ASCII 字符集：字母、数字、符号
ASCII = r'[0-9a-zA-Z!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~]'

#修复两种方向的空格
_RE_CJK_THEN_ASCII  = re.compile(rf"({CJK})\s+({ASCII})")
_RE_ASCII_THEN_CJK  = re.compile(rf"({ASCII})\s+({CJK})")
```

## 🐛 已知限制

-目前主要支持Unicode CJK 字符范围，扩展汉字可能需要调整正则
-超长流式响应（>10MB）可能导致内存占用增加
-某些特殊emoji 表情可能影响截断判断

## 🤝 贡献指南

欢迎提交Issue 和Pull Request！

### 开发环境设置

```bash
# Python 3.12+
python --version

#安装开发依赖
pip install -r requirements.txt  # TODO:添加

#运行测试
pytest tests/  # TODO:添加
```

## 📄 License

MIT License -详见[LICENSE](LICENSE)文件

## 🙏 致谢

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - LLM 推理框架基础
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [Qwen3.5](https://qwenlm.github.io/) -优秀的中文大语言模型

## 📧 联系方式

- Issue: GitHub Issues
- Email: <your-email@example.com>

---

**Made with ❤️ for the CJK community**
