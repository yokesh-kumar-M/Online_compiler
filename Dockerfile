FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    dos2unix gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source (frontend/ is excluded via .dockerignore)
COPY . .

RUN mkdir -p /app/logs /app/staticfiles /app/media /app/static \
    && dos2unix /app/scripts/entrypoint.sh \
    && chmod +x /app/scripts/entrypoint.sh \
    && useradd -m -s /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn online_compiler.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 2 --timeout 120 --access-logfile - --error-logfile -"]
