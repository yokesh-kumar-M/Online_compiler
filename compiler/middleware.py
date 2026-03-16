import logging
import time
from django.http import JsonResponse
from django.core.cache import cache

logger = logging.getLogger('compiler')


class RequestLoggingMiddleware:
    """Log all API requests with timing information."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        if request.path.startswith('/api/'):
            logger.info(
                f"{request.method} {request.path} "
                f"status={response.status_code} "
                f"duration={duration:.3f}s "
                f"user={getattr(request, 'user', 'anonymous')} "
                f"ip={self._get_client_ip(request)}"
            )

        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded.split(',')[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR')


class RateLimitMiddleware:
    """Redis-backed rate limiting middleware."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/v1/compiler/execute'):
            ip = self._get_client_ip(request)
            user_id = str(request.user.id) if hasattr(request, 'user') and request.user.is_authenticated else None
            key = f"ratelimit:execute:{user_id or ip}"

            try:
                current = cache.get(key, 0)
                limit = 100 if user_id else 20

                if current >= limit:
                    return JsonResponse({
                        'error': 'Rate limit exceeded. Please try again later.',
                        'retry_after': 3600,
                    }, status=429)

                cache.set(key, current + 1, timeout=3600)
            except Exception:
                pass  # Don't block requests if Redis is down

        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded.split(',')[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR')
