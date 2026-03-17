"""Frontend views. API views are in views_api.py"""
import ast
import os
import re
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

logger = logging.getLogger('compiler')


def _get_frontend_assets():
    """Discover built React assets from the staticfiles/frontend directory."""
    frontend_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'frontend', 'assets')
    js_file = ''
    css_file = ''

    if os.path.isdir(frontend_dir):
        for f in os.listdir(frontend_dir):
            if f.endswith('.js') and f.startswith('index-'):
                js_file = f'frontend/assets/{f}'
            elif f.endswith('.css') and f.startswith('index-'):
                css_file = f'frontend/assets/{f}'

    return js_file, css_file


def index(request):
    """Render the main compiler page with React frontend."""
    js_file, css_file = _get_frontend_assets()
    return render(request, 'compiler/index.html', {
        'title': 'CodeForge | Online Compiler Enterprise',
        'js_file': js_file,
        'css_file': css_file,
    })


@require_http_methods(["POST"])
def validate_code(request):
    """Validate Python code syntax without executing."""
    try:
        code = request.POST.get('code', '').strip()
        if not code:
            return JsonResponse({'valid': True, 'message': 'No code to validate'})

        try:
            ast.parse(code)
            return JsonResponse({'valid': True, 'message': 'Code is valid'})
        except SyntaxError as e:
            return JsonResponse({'valid': False, 'message': f'Syntax Error: {str(e)}'})
    except Exception as e:
        return JsonResponse({'valid': False, 'message': f'Validation Error: {str(e)}'})
