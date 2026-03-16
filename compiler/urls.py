from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('validate/', views.validate_code, name='validate_code'),
]
