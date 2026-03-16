"""Frontend views. API views are in views_api.py"""
import ast
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

logger = logging.getLogger('compiler')


def index(request):
    """Render the main compiler page."""
    return render(request, 'compiler/index.html', {
        'title': 'Online Compiler Enterprise',
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
