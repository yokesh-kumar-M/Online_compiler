from django.urls import path
from . import views_api

app_name = 'compiler_api'

urlpatterns = [
    path('execute/', views_api.execute_code, name='execute'),
    path('languages/', views_api.get_languages, name='languages'),
    path('examples/', views_api.get_examples, name='examples'),
    path('health/', views_api.health_status, name='health'),
]
