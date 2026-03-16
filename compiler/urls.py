from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Legacy endpoints (redirect to API)
    path('run/', views.run_code, name='run_code'),
    path('validate/', views.validate_code, name='validate_code'),
    path('save/', views.save_code, name='save_code'),
    path('load/', views.load_code, name='load_code'),
    path('list-saved/', views.list_saved_codes, name='list_saved_codes'),
    path('examples/', views.get_examples_legacy, name='get_examples'),
]
