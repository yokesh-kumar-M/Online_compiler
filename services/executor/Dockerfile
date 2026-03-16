FROM python:3.12-slim

# Install compilers for multi-language support
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ default-jdk nodejs npm golang-go \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Create non-root user for security
RUN useradd -m -s /bin/bash executor
USER executor

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
