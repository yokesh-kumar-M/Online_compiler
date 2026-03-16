from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.SnippetViewSet, basename='snippet')
router.register(r'history', views.ExecutionHistoryViewSet, basename='execution-history')

app_name = 'snippets'
urlpatterns = [
    path('', include(router.urls)),
]
