# compiler/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('run/', views.run_code, name='run_code'),
    path('validate/', views.validate_code, name='validate_code'),
    path('save/', views.save_code, name='save_code'),
    path('load/', views.load_code, name='load_code'),
    path('list-saved/', views.list_saved_codes, name='list_saved_codes'),
    path('examples/', views.get_examples, name='get_examples'),
]