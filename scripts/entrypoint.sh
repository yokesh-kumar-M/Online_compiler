#!/bin/bash
set -e

echo "=== Starting Online Compiler Enterprise ==="

# Create required directories
mkdir -p /app/static /app/staticfiles /app/media /app/logs

# Wait for database
echo "Waiting for PostgreSQL..."
for i in $(seq 1 30); do
    if python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_compiler.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
" 2>/dev/null; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "  Attempt $i/30 - waiting..."
    sleep 3
done

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Create superuser (non-critical)
echo "Setting up initial data..."
python manage.py shell -c "
from accounts.models import User
import os
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@compiler.dev')
pw = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'AdminPass123!')
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(email=email, username=email.split('@')[0], password=pw, role='admin')
    print('Superuser created:', email)
else:
    print('Superuser exists')
" || echo "WARNING: Superuser setup skipped"

# Seed languages (non-critical)
python manage.py shell -c "
from compiler.models import SupportedLanguage
data = [
    ('python','Python','3.12','.py',10,128),
    ('javascript','JavaScript','Node 22','.js',10,128),
    ('c','C','GCC 13','.c',10,128),
    ('cpp','C++','G++ 13','.cpp',10,128),
    ('java','Java','21','.java',15,256),
    ('go','Go','1.22','.go',10,128),
]
for n,d,v,e,t,m in data:
    SupportedLanguage.objects.update_or_create(name=n, defaults={'display_name':d,'version':v,'file_extension':e,'timeout_seconds':t,'memory_limit_mb':m,'is_active':True})
print('Languages seeded')
" || echo "WARNING: Language seeding skipped"

echo "=== Ready! Starting server ==="

exec "$@"
