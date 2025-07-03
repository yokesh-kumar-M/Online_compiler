# compiler/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import subprocess
import tempfile
import os
import signal
import threading
import time
import json
import ast
import sys
from io import StringIO
import contextlib

class CodeExecutor:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.restricted_imports = {
            'os', 'subprocess', 'sys', 'importlib', '__import__',
            'eval', 'exec', 'compile', 'open', 'file', 'input',
            'raw_input', 'reload', 'vars', 'dir', 'globals', 'locals'
        }
        self.max_output_size = 10000  # 10KB max output
    
    def validate_code(self, code):
        """Basic code validation to prevent dangerous operations"""
        try:
            # Parse the code to check for dangerous patterns
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.restricted_imports:
                            return False, f"Import '{alias.name}' is not allowed"
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.restricted_imports:
                        return False, f"Import from '{node.module}' is not allowed"
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in self.restricted_imports:
                        return False, f"Function '{node.func.id}' is not allowed"
            return True, "Code is valid"
        except SyntaxError as e:
            return False, f"Syntax Error: {str(e)}"
        except Exception as e:
            return False, f"Validation Error: {str(e)}"
    
    def execute_code_safe(self, code):
        """Execute code in a controlled environment"""
        try:
            # Create a controlled environment
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'sorted': sorted,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'pow': pow,
                    'divmod': divmod,
                    'isinstance': isinstance,
                    'type': type,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                    'delattr': delattr,
                    'chr': chr,
                    'ord': ord,
                    'hex': hex,
                    'oct': oct,
                    'bin': bin,
                    'repr': repr,
                    'ascii': ascii,
                    'format': format,
                    'slice': slice,
                    'reversed': reversed,
                    'any': any,
                    'all': all,
                    'filter': filter,
                    'map': map,
                    'iter': iter,
                    'next': next,
                    'Exception': Exception,
                    'ValueError': ValueError,
                    'TypeError': TypeError,
                    'IndexError': IndexError,
                    'KeyError': KeyError,
                    'AttributeError': AttributeError,
                    'ZeroDivisionError': ZeroDivisionError,
                    'ImportError': ImportError,
                    'NameError': NameError,
                    'StopIteration': StopIteration,
                    'RuntimeError': RuntimeError,
                }
            }
            
            # Capture output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_capture = StringIO()
            stderr_capture = StringIO()
            
            try:
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
                
                # Execute the code
                exec(code, safe_globals)
                
                output = stdout_capture.getvalue()
                error = stderr_capture.getvalue()
                
                if error:
                    return False, error
                
                # Limit output size
                if len(output) > self.max_output_size:
                    output = output[:self.max_output_size] + "\n... (output truncated)"
                
                return True, output
                
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
        except Exception as e:
            return False, f"Runtime Error: {str(e)}"
    
    def execute_code_subprocess(self, code):
        """Execute code using subprocess with timeout"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute with timeout
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tempfile.gettempdir()
                )
                
                output = result.stdout
                error = result.stderr
                
                if result.returncode != 0:
                    return False, error if error else "Program exited with non-zero code"
                
                # Limit output size
                if len(output) > self.max_output_size:
                    output = output[:self.max_output_size] + "\n... (output truncated)"
                
                return True, output
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return False, f"Execution timed out after {self.timeout} seconds"
        except Exception as e:
            return False, f"Execution Error: {str(e)}"

def index(request):
    """Render the main compiler page"""
    context = {
        'title': 'Advanced Python Online Compiler',
        'languages': ['python'],  # Can be extended for more languages
    }
    return render(request, 'compiler/index.html', context)

@require_http_methods(["POST"])
def run_code(request):
    """Execute Python code and return results"""
    try:
        code = request.POST.get('code', '').strip()
        execution_mode = request.POST.get('mode', 'safe')  # 'safe' or 'subprocess'
        
        if not code:
            return JsonResponse({
                'success': False,
                'error': 'No code provided'
            })
        
        # Initialize executor
        executor = CodeExecutor(timeout=10)
        
        # Validate code first
        is_valid, validation_message = executor.validate_code(code)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': validation_message
            })
        
        # Execute code based on mode
        if execution_mode == 'subprocess':
            success, output = executor.execute_code_subprocess(code)
        else:
            success, output = executor.execute_code_safe(code)
        
        return JsonResponse({
            'success': success,
            'output': output,
            'error': None if success else output
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server Error: {str(e)}'
        })

@require_http_methods(["POST"])
def validate_code(request):
    """Validate Python code without executing"""
    try:
        code = request.POST.get('code', '').strip()
        
        if not code:
            return JsonResponse({
                'valid': True,
                'message': 'No code to validate'
            })
        
        executor = CodeExecutor()
        is_valid, message = executor.validate_code(code)
        
        return JsonResponse({
            'valid': is_valid,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'message': f'Validation Error: {str(e)}'
        })

def save_code(request):
    """Save code to session (temporary storage)"""
    if request.method == 'POST':
        code = request.POST.get('code', '')
        filename = request.POST.get('filename', 'untitled.py')
        
        # Save to session
        if 'saved_codes' not in request.session:
            request.session['saved_codes'] = {}
        
        request.session['saved_codes'][filename] = code
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': f'Code saved as {filename}'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def load_code(request):
    """Load saved code from session"""
    if request.method == 'POST':
        filename = request.POST.get('filename', '')
        
        saved_codes = request.session.get('saved_codes', {})
        
        if filename in saved_codes:
            return JsonResponse({
                'success': True,
                'code': saved_codes[filename]
            })
        
        return JsonResponse({
            'success': False,
            'message': 'File not found'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def list_saved_codes(request):
    """List all saved codes"""
    saved_codes = request.session.get('saved_codes', {})
    
    return JsonResponse({
        'success': True,
        'files': list(saved_codes.keys())
    })

def get_examples(request):
    """Get code examples"""
    examples = {
        'hello_world': {
            'title': 'Hello World',
            'code': '''# Hello World Example
print("Hello, World!")
print("Welcome to Python Online Compiler!")
'''
        },
        'fibonacci': {
            'title': 'Fibonacci Sequence',
            'code': '''# Fibonacci Sequence
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Generate first 10 Fibonacci numbers
print("First 10 Fibonacci numbers:")
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
'''
        },
        'data_structures': {
            'title': 'Data Structures Demo',
            'code': '''# Data Structures Examples

# Lists
numbers = [1, 2, 3, 4, 5]
print("List:", numbers)
print("Reversed:", numbers[::-1])

# Dictionaries
person = {"name": "Alice", "age": 30, "city": "New York"}
print("Person:", person)

# Sets
unique_numbers = {1, 2, 3, 3, 4, 5}
print("Unique numbers:", unique_numbers)

# List comprehension
squares = [x**2 for x in range(1, 6)]
print("Squares:", squares)
'''
        },
        'algorithms': {
            'title': 'Sorting Algorithms',
            'code': '''# Bubble Sort Algorithm
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Test the algorithm
numbers = [64, 34, 25, 12, 22, 11, 90]
print("Original array:", numbers)
sorted_numbers = bubble_sort(numbers.copy())
print("Sorted array:", sorted_numbers)
'''
        }
    }
    
    return JsonResponse({
        'success': True,
        'examples': examples
    })