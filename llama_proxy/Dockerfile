FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn[standard] httpx

COPY llama_proxy.py .

EXPOSE 8081

CMD ["python", "llama_proxy.py"]
