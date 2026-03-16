"""Legacy views + frontend serving. API views are in views_api.py"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .executor_client import ExecutorClient
import ast
import logging

logger = logging.getLogger('compiler')


def index(request):
    """Render the main compiler page."""
    return render(request, 'compiler/index.html', {
        'title': 'Online Compiler Enterprise',
    })


@require_http_methods(["POST"])
def run_code(request):
    """Legacy endpoint - execute Python code."""
    try:
        code = request.POST.get('code', '').strip()
        if not code:
            return JsonResponse({'success': False, 'error': 'No code provided'})

        client = ExecutorClient()
        result = client.execute(code, 'python')

        return JsonResponse({
            'success': result['success'],
            'output': result.get('output', ''),
            'error': result.get('error', None) if not result['success'] else None,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server Error: {str(e)}'})


@require_http_methods(["POST"])
def validate_code(request):
    """Validate Python code without executing."""
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


def save_code(request):
    if request.method == 'POST':
        code = request.POST.get('code', '')
        filename = request.POST.get('filename', 'untitled.py')
        if 'saved_codes' not in request.session:
            request.session['saved_codes'] = {}
        request.session['saved_codes'][filename] = code
        request.session.modified = True
        return JsonResponse({'success': True, 'message': f'Code saved as {filename}'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def load_code(request):
    if request.method == 'POST':
        filename = request.POST.get('filename', '')
        saved_codes = request.session.get('saved_codes', {})
        if filename in saved_codes:
            return JsonResponse({'success': True, 'code': saved_codes[filename]})
        return JsonResponse({'success': False, 'message': 'File not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def list_saved_codes(request):
    saved_codes = request.session.get('saved_codes', {})
    return JsonResponse({'success': True, 'files': list(saved_codes.keys())})


def get_examples_legacy(request):
    examples = {
        'hello_world': {'title': 'Hello World', 'code': 'print("Hello, World!")'},
        'fibonacci': {'title': 'Fibonacci', 'code': 'def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)\n\nfor i in range(10):\n    print(f"F({i}) = {fib(i)}")'},
        'data_structures': {'title': 'Data Structures', 'code': 'nums = [1,2,3,4,5]\nprint("List:", nums)\nprint("Reversed:", nums[::-1])'},
        'algorithms': {'title': 'Sorting', 'code': 'def sort(a):\n    for i in range(len(a)):\n        for j in range(len(a)-i-1):\n            if a[j]>a[j+1]: a[j],a[j+1]=a[j+1],a[j]\n    return a\nprint(sort([64,34,25,12,22,11,90]))'},
    }
    return JsonResponse({'success': True, 'examples': examples})
