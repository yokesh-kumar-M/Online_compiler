#!/bin/bash
# =============================================================================
# Online Compiler Enterprise - Entrypoint Script
# =============================================================================
set -e

echo "🚀 Starting Online Compiler Enterprise..."

# Wait for database
echo "⏳ Waiting for PostgreSQL..."
while ! python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB', 'online_compiler'),
        user=os.environ.get('POSTGRES_USER', 'compiler_admin'),
        password=os.environ.get('POSTGRES_PASSWORD', 'devpassword123'),
        host=os.environ.get('POSTGRES_HOST', 'postgres'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
    )
    conn.close()
except Exception:
    exit(1)
" 2>/dev/null; do
    echo "  PostgreSQL not ready, retrying in 2s..."
    sleep 2
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis
echo "⏳ Waiting for Redis..."
while ! python -c "
import redis
import os
r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
r.ping()
" 2>/dev/null; do
    echo "  Redis not ready, retrying in 2s..."
    sleep 2
done
echo "✅ Redis is ready!"

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
echo "👤 Creating superuser (if not exists)..."
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@compiler.dev',
        username='admin',
        password='AdminPass123!@#',
        role='admin',
    )
    print('  ✅ Superuser created: admin@compiler.dev / AdminPass123!@#')
else:
    print('  ℹ️  Superuser already exists')
"

# Seed supported languages
echo "🔧 Seeding supported languages..."
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
        name=name,
        defaults={'display_name': display, 'version': version, 'file_extension': ext,
                  'timeout_seconds': timeout, 'memory_limit_mb': mem, 'is_active': True}
    )
print('  ✅ Languages seeded')
"

echo "🎉 Online Compiler Enterprise is ready!"
echo "   Gateway:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs/"
echo "   Admin:    http://localhost:8000/admin/"

# Start the server
exec "$@"
