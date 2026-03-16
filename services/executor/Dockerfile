FROM python:3.12-slim

# Install lightweight compilers only (free tier friendly)
# gcc/g++ for C/C++, nodejs for JavaScript
# Note: Java and Go omitted to keep image under 512MB for Render free tier
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Create non-root user for security
RUN useradd -m -s /bin/bash executor
USER executor

EXPOSE 8001

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001} --workers 2"]
