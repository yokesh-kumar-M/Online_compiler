#!/bin/bash
set -e

echo "Starting Online Compiler Enterprise..."

# Create required directories
mkdir -p /app/static /app/staticfiles /app/media /app/logs

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
MAX_RETRIES=30
RETRY_COUNT=0
until python manage.py check --database default 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "ERROR: Database not available after $MAX_RETRIES retries"
        exit 1
    fi
    echo "  Database not ready ($RETRY_COUNT/$MAX_RETRIES)..."
    sleep 3
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
echo "Creating superuser (if not exists)..."
python manage.py shell << 'EOF'
from accounts.models import User
import os
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@compiler.dev")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "AdminPass123!")
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(email=email, username=email.split("@")[0], password=password, role="admin")
    print("Superuser created:", email)
else:
    print("Superuser already exists")
EOF

# Seed supported languages
echo "Seeding supported languages..."
python manage.py shell << 'EOF'
from compiler.models import SupportedLanguage
langs = [
    {"name": "python", "display_name": "Python", "version": "3.12", "file_extension": ".py", "timeout_seconds": 10, "memory_limit_mb": 128},
    {"name": "javascript", "display_name": "JavaScript", "version": "Node 22", "file_extension": ".js", "timeout_seconds": 10, "memory_limit_mb": 128},
    {"name": "c", "display_name": "C", "version": "GCC 13", "file_extension": ".c", "timeout_seconds": 10, "memory_limit_mb": 128},
    {"name": "cpp", "display_name": "C++", "version": "G++ 13", "file_extension": ".cpp", "timeout_seconds": 10, "memory_limit_mb": 128},
    {"name": "java", "display_name": "Java", "version": "21", "file_extension": ".java", "timeout_seconds": 15, "memory_limit_mb": 256},
    {"name": "go", "display_name": "Go", "version": "1.22", "file_extension": ".go", "timeout_seconds": 10, "memory_limit_mb": 128},
]
for lang in langs:
    name = lang.pop("name")
    SupportedLanguage.objects.update_or_create(name=name, defaults=lang)
print("Languages seeded")
EOF

echo "Online Compiler Enterprise is ready!"

# Start the server
exec "$@"
