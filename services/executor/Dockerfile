FROM python:3.12-slim

# Language runtimes/compilers the FastAPI executor invokes via subprocess:
#   - gcc / g++  (C, C++)
#   - default-jdk-headless (Java: javac, java)
#   - nodejs (JavaScript)
#   - golang-go (Go)
# Heads-up: this image will be ~1.5GB. Render free tier docker builds handle
# it, but cold builds take 5-10 minutes.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libc6-dev \
        default-jdk-headless \
        nodejs \
        golang-go \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Go needs a writable cache dir; pre-create one owned by the non-root user.
RUN useradd -m -s /bin/bash executor \
    && mkdir -p /home/executor/.cache/go-build /home/executor/go \
    && chown -R executor:executor /home/executor

ENV GOCACHE=/home/executor/.cache/go-build
ENV GOPATH=/home/executor/go
ENV HOME=/home/executor

USER executor

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --workers 1"]
