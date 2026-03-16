#!/usr/bin/env bash
# =============================================================================
# Render Build Script - Online Compiler Enterprise
# This script runs during every Render deploy
# =============================================================================
set -o errexit

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Creating superuser (if not exists)..."
python manage.py shell -c "
from accounts.models import User
import os
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@compiler.dev')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'AdminPass123!')
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email=email,
        username=email.split('@')[0],
        password=password,
        role='admin',
    )
    print(f'Superuser created: {email}')
else:
    print('Superuser already exists')
"

echo "==> Seeding supported languages..."
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
print('Languages seeded successfully')
"

echo "==> Build complete!"
