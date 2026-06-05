#!/bin/bash
#快速启动脚本- Quick Start Script

set -e

echo "======================================"
echo "  CJK Whitespace Proxy - Startup"
echo "======================================"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

echo "✅ Docker and Docker Compose are ready"
echo ""

# Check if .env file exists, if not copy from example
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for service to be ready
echo "Waiting for services to start..."
sleep 5

# Check if proxy is responding
if curl -s http://localhost:58080/v1/models &> /dev/null; then
    echo ""
    echo "✅ Services started successfully!"
    echo ""
    echo "📌 Proxy service: http://localhost:58080"
    echo "📌 Logs: docker-compose logs -f llama-proxy"
    echo "📌 Stop: docker-compose down"
else
    echo ""
    echo "⚠️  Service might not be ready yet. Check with:"
    echo "   curl http://localhost:58080/v1/models"
fi
