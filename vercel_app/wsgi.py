"""
Vercel Serverless Handler for Django
=====================================
NOTE: Vercel is NOT ideal for Django. Limitations:
  - 10s function timeout (code execution will fail)
  - No persistent file system
  - No background workers (Celery won't work)
  - Cold starts add latency
  - No WebSocket support

RECOMMENDED: Use Render.com instead for full Django deployment.
This Vercel config is provided for DEMO/FRONTEND-ONLY purposes.

For a proper setup, deploy the frontend separately on Vercel
and point API calls to the Render backend.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_compiler.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel requires a handler named 'app' or 'handler'
app = application
