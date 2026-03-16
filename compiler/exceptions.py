import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('compiler')


def custom_exception_handler(exc, context):
    """Enterprise exception handler with structured error responses."""
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': {
                'status_code': response.status_code,
                'message': _get_error_message(response),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data},
            }
        }
        response.data = error_data
    else:
        logger.exception(f"Unhandled exception: {exc}")
        response = Response({
            'error': {
                'status_code': 500,
                'message': 'An internal server error occurred.',
                'details': {},
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def _get_error_message(response):
    status_messages = {
        400: 'Bad Request',
        401: 'Authentication required',
        403: 'Permission denied',
        404: 'Resource not found',
        405: 'Method not allowed',
        429: 'Rate limit exceeded',
        500: 'Internal server error',
    }
    return status_messages.get(response.status_code, 'An error occurred')
