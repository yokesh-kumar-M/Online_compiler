from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def health_check_view(request):
    """Simple health check endpoint."""
    return JsonResponse({'status': 'healthy'})


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/compiler/', include('compiler.urls_api')),
    path('api/v1/snippets/', include('snippets.urls')),

    # OAuth2 Provider
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    # Health Check
    path('health/', health_check_view, name='health_check'),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Frontend (catch-all last)
    path('', include('compiler.urls')),
]
