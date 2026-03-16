"""REST API views for the compiler service."""
import logging
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from drf_spectacular.utils import extend_schema

from .executor_client import ExecutorClient
from snippets.models import ExecutionHistory

logger = logging.getLogger('compiler')


class CodeExecutionThrottle(UserRateThrottle):
    rate = '30/hour'
    scope = 'code_execution'


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'code': {'type': 'string', 'description': 'Source code to execute'},
                'language': {'type': 'string', 'default': 'python'},
                'stdin': {'type': 'string', 'default': ''},
            },
            'required': ['code'],
        }
    },
    responses={200: {
        'type': 'object',
        'properties': {
            'success': {'type': 'boolean'},
            'output': {'type': 'string'},
            'error': {'type': 'string'},
            'execution_time_ms': {'type': 'integer'},
            'execution_id': {'type': 'string'},
        }
    }},
    description='Execute code synchronously and return results.',
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([CodeExecutionThrottle])
def execute_code(request):
    """Execute code and return results synchronously."""
    code = request.data.get('code', '').strip()
    language = request.data.get('language', 'python')
    stdin = request.data.get('stdin', '')

    if not code:
        return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)

    if len(code) > 50000:
        return Response({'error': 'Code exceeds maximum size (50KB)'}, status=status.HTTP_400_BAD_REQUEST)

    # Check user execution limits
    user = request.user if request.user.is_authenticated else None
    if user and hasattr(user, 'can_execute') and not user.can_execute:
        return Response({
            'error': 'Daily execution limit reached. Upgrade your plan for more executions.',
            'limit': user.execution_limit,
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # Execute via microservice
    client = ExecutorClient()
    result = client.execute(code, language, stdin)

    # Record execution history
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in ip:
        ip = ip.split(',')[0].strip()

    execution = ExecutionHistory.objects.create(
        user=user,
        code=code,
        language=language,
        status='success' if result['success'] else 'error',
        output=result.get('output', ''),
        error_output=result.get('error', ''),
        execution_time_ms=result.get('execution_time_ms', 0),
        ip_address=ip or None,
    )

    # Update user stats
    if user:
        from django.db.models import F
        from accounts.models import User
        User.objects.filter(pk=user.pk).update(
            total_executions=F('total_executions') + 1,
            executions_today=F('executions_today') + 1,
            last_execution_at=timezone.now(),
        )

    return Response({
        'success': result['success'],
        'output': result.get('output', ''),
        'error': result.get('error', ''),
        'execution_time_ms': result.get('execution_time_ms', 0),
        'execution_id': str(execution.id),
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_languages(request):
    """Get supported programming languages."""
    client = ExecutorClient()
    languages = client.get_supported_languages()
    return Response({'languages': languages})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_examples(request):
    """Get code examples for each language."""
    examples = {
        'hello_world': {
            'title': 'Hello World',
            'language': 'python',
            'code': '# Hello World\nprint("Hello, World!")\nprint("Welcome to the Online Compiler!")\n',
        },
        'fibonacci': {
            'title': 'Fibonacci Sequence',
            'language': 'python',
            'code': 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nfor i in range(10):\n    print(f"F({i}) = {fibonacci(i)}")\n',
        },
        'data_structures': {
            'title': 'Data Structures',
            'language': 'python',
            'code': '# Lists\nnumbers = [1, 2, 3, 4, 5]\nprint("List:", numbers)\nprint("Reversed:", numbers[::-1])\n\n# Dictionaries\nperson = {"name": "Alice", "age": 30}\nprint("Person:", person)\n\n# Set\nunique = {1, 2, 3, 3, 4}\nprint("Set:", unique)\n\n# List comprehension\nsquares = [x**2 for x in range(1, 6)]\nprint("Squares:", squares)\n',
        },
        'sorting': {
            'title': 'Sorting Algorithm',
            'language': 'python',
            'code': 'def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n    return arr\n\nnumbers = [64, 34, 25, 12, 22, 11, 90]\nprint("Original:", numbers)\nprint("Sorted:", bubble_sort(numbers.copy()))\n',
        },
    }
    return Response({'success': True, 'examples': examples})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_status(request):
    """Get system health status."""
    client = ExecutorClient()
    executor_healthy = client.health_check()

    return Response({
        'status': 'healthy',
        'services': {
            'gateway': True,
            'executor': executor_healthy,
            'database': True,
        },
        'timestamp': timezone.now().isoformat(),
    })
