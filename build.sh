#!/usr/bin/env bash
# =============================================================================
# Render Build Script - Online Compiler Enterprise
# =============================================================================
set -o errexit

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Creating required directories..."
mkdir -p static staticfiles media logs

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Creating superuser (if not exists)..."
python manage.py shell <<'PYEOF'
import os
from accounts.models import User

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
PYEOF

echo "==> Seeding supported languages..."
python manage.py shell <<'PYEOF'
from compiler.models import SupportedLanguage

languages = [
    {
        'name': 'python',
        'display_name': 'Python',
        'version': '3.12',
        'file_extension': '.py',
        'timeout_seconds': 10,
        'memory_limit_mb': 128,
        'template_code': 'print("Hello, World!")',
    },
    {
        'name': 'javascript',
        'display_name': 'JavaScript',
        'version': 'Node 22',
        'file_extension': '.js',
        'timeout_seconds': 10,
        'memory_limit_mb': 128,
        'template_code': 'console.log("Hello, World!");',
    },
    {
        'name': 'c',
        'display_name': 'C',
        'version': 'GCC 13',
        'file_extension': '.c',
        'timeout_seconds': 10,
        'memory_limit_mb': 128,
        'template_code': '#include <stdio.h>\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}',
    },
    {
        'name': 'cpp',
        'display_name': 'C++',
        'version': 'G++ 13',
        'file_extension': '.cpp',
        'timeout_seconds': 10,
        'memory_limit_mb': 128,
        'template_code': '#include <iostream>\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}',
    },
    {
        'name': 'java',
        'display_name': 'Java',
        'version': '21',
        'file_extension': '.java',
        'timeout_seconds': 15,
        'memory_limit_mb': 256,
        'template_code': 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
    },
    {
        'name': 'go',
        'display_name': 'Go',
        'version': '1.22',
        'file_extension': '.go',
        'timeout_seconds': 10,
        'memory_limit_mb': 128,
        'template_code': 'package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hello, World!")\n}',
    },
]

for lang in languages:
    name = lang.pop('name')
    obj, created = SupportedLanguage.objects.update_or_create(name=name, defaults=lang)
    status = 'created' if created else 'updated'
    print(f'  {status}: {obj.display_name}')

print('Languages seeded successfully')
PYEOF

echo "==> Build complete!"
