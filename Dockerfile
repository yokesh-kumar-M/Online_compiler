# Stage 1: Build the React Frontend
FROM node:22-slim AS frontend-builder
WORKDIR /app/frontend
# Copy package files (from the frontend directory)
COPY frontend/package.json frontend/package-lock.json* ./
# Install dependencies
RUN npm install --legacy-peer-deps
# Copy the rest of the frontend source
COPY frontend/ ./
# Build the Vite app
RUN npm run build

# Stage 2: Build the Django Backend
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend assets from Stage 1 into the location Django expects
RUN mkdir -p /app/logs /app/staticfiles/frontend /app/media /app/static
COPY --from=frontend-builder /app/frontend/dist /app/staticfiles/frontend

RUN dos2unix /app/scripts/entrypoint.sh && chmod +x /app/scripts/entrypoint.sh

RUN useradd -m -s /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn online_compiler.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 2 --timeout 120 --access-logfile - --error-logfile -"]
