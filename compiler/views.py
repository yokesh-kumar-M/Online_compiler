"""Frontend-facing views. JSON API views live in views_api.py."""
import ast
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def index(request):
    """Root landing page.

    The React frontend is hosted on Vercel; this Django service is the API.
    Return a small JSON payload so root hits aren't a 404, and so health
    probes / curl smoke-tests get a useful response.
    """
    frontend_url = os.environ.get('FRONTEND_URL', '')
    return JsonResponse({
        'service': 'online-compiler-gateway',
        'status': 'ok',
        'frontend': frontend_url or 'configure FRONTEND_URL env var',
        'docs': request.build_absolute_uri('/api/docs/'),
        'health': request.build_absolute_uri('/health/'),
    })


@require_http_methods(["POST"])
def validate_code(request):
    """Validate Python code syntax without executing."""
    code = request.POST.get('code', '').strip()
    if not code:
        return JsonResponse({'valid': True, 'message': 'No code to validate'})

    try:
        ast.parse(code)
        return JsonResponse({'valid': True, 'message': 'Code is valid'})
    except SyntaxError as e:
        return JsonResponse({'valid': False, 'message': f'Syntax Error: {str(e)}'})
