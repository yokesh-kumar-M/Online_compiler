# compiler/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),       # Loads the HTML page
    path('run/', views.run_code, name='run_code'),  # Processes the submitted code
]
