# compiler/views.py
from django.shortcuts import render
from django.http import JsonResponse
import subprocess

def index(request):
    return render(request, 'compiler/index.html')

def run_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            result = subprocess.run(
                ['python', '-c', code],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            output = "Execution timed out!"
        return JsonResponse({'output': output})

    return JsonResponse({'error': 'Only POST requests are allowed!'}, status=400)