#内网部署指南（中文版）

## 📋 目录

1. [环境准备](#环境准备)
2. [网络配置说明](#网络配置说明)
3. [三种部署方案](#三种部署方案)
4. [常见问题排查](#常见问题排查)
5. [性能优化建议](#性能优化建议)

---

##环境准备

###硬件要求

|组件|最低配置|推荐配置|
|------|----------|--------|
|CPU |4 核|8 核以上|
|内存|16GB |32GB+ |
|GPU |NVIDIA RTX 3090 (24GB) |RTX 4090 / A100 |
|磁盘|50GB SSD |200GB NVMe SSD |

###软件要求

- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Driver（如果使用GPU）
- Python 3.10+（本地部署）

---

##网络配置说明

###为什么需要代理？

在中国大陆或企业内网环境中，以下服务可能无法直接访问：

|服务|用途|是否需要代理|
|------|------|-------------|
|HuggingFace |下载GGUF 模型文件|✅必需|
|PyPI (pypi.org) |安装Python 依赖包|✅推荐|
|GitHub |克隆代码仓库|可选|
|Docker Hub |拉取Docker 镜像|可选（有国内镜像）|

###代理类型说明

####1. Build Args 代理（docker-compose.yaml 中的args）

```yaml
build:
  args:
    - HTTP_PROXY=http://proxy-server:8087
    - HTTPS_PROXY=http://proxy-server:8087
```

**用途：**
- Docker 构建时下载Python 包（FastAPI、uvicorn 等）
-从HuggingFace 下载GGUF 模型文件
- **仅在构建镜像时使用，运行时不生效**

####2. Runtime Environment 代理（docker-compose.yaml 中的environment）

```yaml
environment:
  - HTTP_PROXY=http://proxy-server:8087
  - HTTPS_PROXY=http://proxy-server:8087
```

**用途：**
-容器运行时的HTTP/HTTPS 请求
-用于访问外部API（如HuggingFace Inference）
- **运行时生效**

####3. Host 环境变量（.env 文件）

```bash
# .env 文件
HTTP_PROXY=http://proxy-server:8087
HTTPS_PROXY=http://proxy-server:8087
HF_ENDPOINT=https://hf-mirror.com
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

**用途：**
- Docker Compose 会自动将.env 中的变量注入容器
-方便集中管理和修改配置

---

##三种部署方案

###方案一：使用HF Mirror +清华源（最简单）

适合大多数中国用户，无需搭建私有代理服务器。

####步骤

```bash
#1.克隆项目
git clone <your-repo-url>
cd llama-proxy-for-qwen3.5-9b

#2.创建.env 文件并配置镜像源
cat > .env << 'EOF'
# Docker Compose 构建代理（可选，如果HF Mirror 可用可不配）
HTTP_PROXY=
HTTPS_PROXY=

# HuggingFace 镜像源（推荐）
HF_ENDPOINT=https://hf-mirror.com

# Python 包镜像源（清华）
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# LLM 配置
LLAMA_API_KEY=${LLAMA_API_KEY:-your-api-key}
EOF

#3.修改docker-compose.yaml，添加HF_ENDPOINT 环境变量支持
#在llama-cpp 服务中添加：
environment:
  - HF_ENDPOINT=https://hf-mirror.com

#4.启动服务（会自动使用镜像源下载）
docker-compose up -d
```

####优点

- ✅ 无需搭建代理服务器
- ✅ 配置简单，一行命令搞定
- ✅ 速度较快（国内节点）

####缺点

- ⚠️ 需要HF Mirror 保持同步（目前稳定）
- ⚠️ 某些新模型可能镜像中还没有

---

###方案二：使用私有代理服务器（推荐企业用户）

适合有内部代理服务器的环境，可统一管理网络流量。

####步骤

#####1.搭建代理服务器（可选，已有则跳过）

**使用Squid：**

```bash
#安装squid
apt-get install squid

#编辑配置文件
vim /etc/squid/squid.conf

#添加访问控制
acl localnet src 192.168.0.0/16
http_access allow localnet
http_access deny all

#启动服务
systemctl start squid
```

**或使用aria2c 作为下载代理：**

```bash
#安装aria2c
apt-get install aria2c

#运行代理（支持多线程下载）
aria2c --listen-port=8087 \
       --max-connection-per-server=16 \
       --min-split-size=1M \
       --max-concurrent-downloads=16 \
       --reuse-uri
```

#####2.配置docker-compose.yaml

```yaml
services:
  llama-proxy:
    build:
      args:
        - HTTP_PROXY=http://your-proxy-server:8087
        - HTTPS_PROXY=http://your-proxy-server:8087
    
    environment:
      - UPSTREAM=http://llama-cpp:58080
      - PROXY_PORT=58080
```

#####3.启动服务

```bash
docker-compose up -d
```

####优点

- ✅ 可控性强，可配置缓存
- ✅ 统一管理网络流量
- ✅ 支持断点续传（aria2c）

####缺点

- ⚠️ 需要维护代理服务器
- ⚠️ 配置相对复杂

---

###方案三：离线部署（完全内网环境）

适合没有外网访问权限的纯内网环境。

####步骤

#####1.在外网环境准备所有资源

```bash
#创建资源目录
mkdir -p /tmp/llama-proxy-resources/{models,deps}

#下载模型文件
cd /tmp/llama-proxy-resources/models
aria2c -x 16 -s 16 -k 1M \
  https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/gemma-4-12b-it-Q4_K_M.gguf

#下载Docker 镜像（可选，如果内网有镜像仓库）
docker pull ghcr.io/ggml-org/llama.cpp:full-cuda
docker save ghcr.io/ggml-org/llama.cpp:full-cuda > llama-cpp.tar.gz

#下载Python 依赖包
pip download fastapi uvicorn httpx --no-deps
tar -xzf FastAPI-0.109.0-py3-none-any.whl -C /tmp/llama-proxy-resources/deps
```

#####2.传输资源到内网服务器

```bash
#压缩打包
cd /tmp/llama-proxy-resources
tar -czf llama-proxy-offline.tar.gz --exclude='*.git*' --exclude='__pycache__' .

#传输到内网（使用scp、rsync 等）
scp llama-proxy-offline.tar.gz user@inner-server:/opt/
```

#####3.在内网服务器解压并部署

```bash
cd /opt
tar -xzf llama-proxy-offline.tar.gz

#创建模型目录
mkdir -p /opt/llama-proxy-resources/models
cp /tmp/llama-proxy-resources/models/*.gguf /opt/llama-proxy-resources/models/

#修改docker-compose.yaml，移除代理配置
sed -i '/HTTP_PROXY/d' docker-compose.yaml
sed -i '/HTTPS_PROXY/d' docker-compose.yaml

#启动服务（无需网络）
docker-compose up -d
```

####优点

- ✅ 完全离线，不受网络限制
- ✅ 一次准备，多次部署

####缺点

- ⚠️ 准备工作繁琐
- ⚠️ 需要手动更新模型和依赖

---

##常见问题排查

###问题1：Docker Compose 启动时提示"Image pull failed"

**错误信息：**

```
Error response from daemon: manifest for ghcr.io/ggml-org/llama.cpp:full-cuda not found
```

**原因：**无法访问Docker Hub 或GHCR。

**解决方案：**

```bash
#方法1：使用镜像源
docker pull docker.m.daocloud.io/ghcr.io/ggml-org/llama.cpp:full-cuda

#方法2：手动下载镜像并导入
wget https://example.com/llama-cpp.tar.gz  #从其他地方获取
docker load -i llama-cpp.tar.gz

#方法3：使用离线预构建的docker-compose.yaml（方案三）
```

---

###问题2：pip install 超时或失败

**错误信息：**

```
Could not fetch URL: Connection timed out
```

**原因：** PyPI 服务器无法访问。

**解决方案：**

```bash
#使用清华源
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
pip install fastapi uvicorn[standard] httpx

#或使用阿里源
export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
pip install fastapi uvicorn[standard] httpx

#或使用中科大源
export PIP_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple/
pip install fastapi uvicorn[standard] httpx
```

---

###问题3：HuggingFace 下载速度慢或超时

**错误信息：**

```
403 Client Error: Forbidden for url: https://huggingface.co/...
```

**原因：** IP 被封禁或网络不稳定。

**解决方案：**

```bash
#方法1：使用HF Mirror
export HF_ENDPOINT=https://hf-mirror.com
pip install huggingface_hub[hf_transfer]

#方法2：配置代理
export HTTP_PROXY=http://proxy-server:8087
export HTTPS_PROXY=http://proxy-server:8087

#方法3：使用aria2c 多线程下载（推荐）
aria2c -x 16 -s 16 -k 1M \
  https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/model-Q4_K_M.gguf

#方法4：从国内镜像站下载
wget https://gitee.com/mirrors/pytorch/releases/download/v2.0.0/torch_stable.py
```

---

###问题4：容器无法访问宿主机网络

**错误信息：**

```
host.docker.internal: Name or service not known
```

**原因：** `extra_hosts`配置缺失。

**解决方案：**

确保在docker-compose.yaml 中包含：

```yaml
services:
  llama-proxy:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

然后重启容器：

```bash
docker-compose restart llama-proxy
```

---

###问题5：GPU 无法识别

**错误信息：**

```
NVIDIA container CLI not found in $PATH
```

**原因：** NVIDIA Container Toolkit 未安装。

**解决方案：**

```bash
#安装NVIDIA Container Toolkit
apt-get install -y nvidia-container-toolkit

#重启Docker
systemctl restart docker

#验证GPU 是否可用
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

---

##性能优化建议

###1.模型下载加速

**使用aria2c 多线程下载：**

```bash
aria2c -x 16 -s 16 -k 1M \
  https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/model-Q4_K_M.gguf
```

参数说明：
- `-x 16`：使用16 个连接
- `-s 16`：每个文件分割为16 部分
- `-k 1M`：每块大小为1MB

###2.Docker 镜像缓存

**复用已构建的镜像：**

```bash
#第一次构建会下载基础镜像，后续可直接使用
docker-compose build --no-cache  #首次构建
docker-compose build             #复用缓存（更快）
```

###3.GPU 内存优化

**调整llama.cpp 参数减少内存占用：**

```yaml
command: >
  --server --port 58080
  -ngl 99                    #所有层放到GPU
  -c 131074                  #减小context size（从262144 改为131074）
  --cache-type-k q4_0        #使用更低精度的KV cache
  --cache-type-v q4_0
```

###4.并发请求优化

**限制最大并发数：**

```yaml
#在docker-compose.yaml 中添加健康检查
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:58080/v1/models"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

##附录：快速参考卡片

###一键启动脚本（内网环境）

```bash
#!/bin/bash
# deploy.sh -内网环境快速部署脚本

set -e

echo "🚀 开始部署llama-proxy..."

#检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装Docker"
    exit 1
fi

#创建.env 文件
cat > .env << 'EOF'
HTTP_PROXY=
HTTPS_PROXY=
HF_ENDPOINT=https://hf-mirror.com
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
LLAMA_API_KEY=${LLAMA_API_KEY:-your-api-key}
EOF

echo "✅ 创建配置文件完成"

#启动服务
docker-compose up -d

echo ""
echo "🎉 部署完成！"
echo "   服务地址：http://localhost:58080"
echo "   查看日志：docker-compose logs -f llama-proxy"
echo "   停止服务：docker-compose down"
```

使用方式：

```bash
chmod +x deploy.sh
./deploy.sh
```

---

**Last updated: June 4, 2026**
