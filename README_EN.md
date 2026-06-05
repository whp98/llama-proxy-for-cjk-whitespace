# CJK Whitespace Post-Processing Proxy - llama-proxy

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A transparent proxy for **llama.cpp** that automatically fixes extra whitespace between CJK (Chinese, Japanese, Korean) characters and ASCII text.

## 🌟 Features

- ✨ **Transparent Proxy**: OpenAI API compatible, no client code changes needed
- ⚡ **Streaming Processing**: SSE stream handling with chunk-by-chunk cleanup
- 🔍 **Smart Detection**: Automatically detects CJK↔ASCII boundaries
- 🛡️ **Safe Buffering**: Prevents accidental content truncation
- 🌐 **Multi-format Support**: Compatible with both OpenAI and Anthropic APIs

## 📦 Quick Start

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

The service will start at `http://localhost:58080`.

### Local Installation

```bash
# Install dependencies
pip install fastapi uvicorn[standard] httpx

# Run the proxy
python llama_proxy/llama_proxy.py
```

## 🧪 Usage Example

```bash
curl http://localhost:58080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5-9b",
    "messages": [{"role": "user", "content": "I use Python to calculate"}],
    "stream": true
  }' | head -5
```

**Output example:**
```
data: {"choices":[{"delta":{"content":"我使用Python"}}...]...
data: {"choices":[{"delta":{"content":" code to calculate results"}}...]...
# Notice: No extra space between "Python" and "code"!
```

## 📖 Documentation

|File|Description|
|------|------------|
| [README_CN.md](README_CN.md) |Chinese introduction|
| [GUIDE.md](GUIDE.md) |Detailed usage guide (Chinese)|
| [快速下载.md](快速下载.md) |Quick download links for GGUF models|

## 🛠️ Configuration

### Environment Variables

|Variable|Description|Default|
|---------|------------|--------|
| `UPSTREAM` |Upstream LLM service URL| `http://localhost:58080` |
| `PROXY_PORT` |Proxy listening port| `8081` |
| `LOG_LEVEL` |Logging level| `INFO` |

### Docker Compose Example

```yaml
services:
  llama-proxy:
    build: ./llama_proxy
    environment:
      - UPSTREAM=http://llama-cpp:58080
      - PROXY_PORT=58080
    ports:
      - "58080:58080"
```

## 📁 Project Structure

```
llama-proxy-for-qwen3.5-9b/
├── README.md              # English documentation (this file)
├── README_CN.md           # Chinese introduction
├── GUIDE.md               # Detailed usage guide
├── LICENSE                # MIT License
├── docker-compose.yaml    # Docker configuration
├── 快速下载.md            # Quick download links
└── llama_proxy/          # Proxy code
    ├── Dockerfile         # Docker build file
    └── llama_proxy.py     # Main application code
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/<your-org>/llama-proxy-for-qwen3.5-9b/issues)
- **Email**: <your-email@example.com>

## 🙏 Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - LLM inference framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for APIs
- [Qwen3.5](https://qwenlm.github.io/) - Excellent Chinese language model

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the CJK community**
