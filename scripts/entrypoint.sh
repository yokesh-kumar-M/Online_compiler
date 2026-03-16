#!/bin/bash
set -e

echo "Starting Online Compiler Enterprise..."

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
MAX_RETRIES=30
RETRY_COUNT=0
until python -c "
import os, sys
db_url = os.environ.get('DATABASE_URL', '')
if db_url:
    import dj_database_url
    conf = dj_database_url.parse(db_url)
    import psycopg2
    conn = psycopg2.connect(
        dbname=conf['NAME'], user=conf['USER'], password=conf['PASSWORD'],
        host=conf['HOST'], port=conf['PORT'],
    )
    conn.close()
else:
    import psycopg2
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB', 'online_compiler'),
        user=os.environ.get('POSTGRES_USER', 'compiler_admin'),
        password=os.environ.get('POSTGRES_PASSWORD', 'devpassword123'),
        host=os.environ.get('POSTGRES_HOST', 'postgres'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
    )
    conn.close()
" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "ERROR: PostgreSQL not available after $MAX_RETRIES retries"
        exit 1
    fi
    echo "  PostgreSQL not ready, retrying ($RETRY_COUNT/$MAX_RETRIES)..."
    sleep 2
done
echo "PostgreSQL is ready!"

# Wait for Redis only if REDIS_URL is set
REDIS_URL="${REDIS_URL:-}"
if [ -n "$REDIS_URL" ]; then
    echo "Waiting for Redis..."
    RETRY_COUNT=0
    until python -c "
import redis, os
r = redis.from_url(os.environ.get('REDIS_URL'))
r.ping()
" 2>/dev/null; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo "WARNING: Redis not available, continuing without it"
            break
        fi
        echo "  Redis not ready, retrying ($RETRY_COUNT/$MAX_RETRIES)..."
        sleep 2
    done
    echo "Redis is ready!"
else
    echo "No REDIS_URL set, skipping Redis check"
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
mkdir -p /app/static /app/staticfiles /app/media /app/logs
python manage.py collectstatic --noinput

# Create superuser if needed
echo "Creating superuser (if not exists)..."
python manage.py shell -c "
from accounts.models import User
import os
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@compiler.dev')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'AdminPass123!')
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(email=email, username=email.split('@')[0], password=password, role='admin')
    print('Superuser created:', email)
else:
    print('Superuser already exists')
"

# Seed supported languages
echo "Seeding supported languages..."
python manage.py shell -c "
from compiler.models import SupportedLanguage
languages = [
    ('python', 'Python', '3.12', '.py', 10, 128),
    ('javascript', 'JavaScript', 'Node 22', '.js', 10, 128),
    ('c', 'C', 'GCC 13', '.c', 10, 128),
    ('cpp', 'C++', 'G++ 13', '.cpp', 10, 128),
    ('java', 'Java', '21', '.java', 15, 256),
    ('go', 'Go', '1.22', '.go', 10, 128),
]
for name, display, version, ext, timeout, mem in languages:
    SupportedLanguage.objects.update_or_create(
        name=name, defaults={'display_name': display, 'version': version,
        'file_extension': ext, 'timeout_seconds': timeout,
        'memory_limit_mb': mem, 'is_active': True})
print('Languages seeded')
"

echo "Online Compiler Enterprise is ready!"

# Start the server
exec "$@"
