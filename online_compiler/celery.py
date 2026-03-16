import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_compiler.settings')

app = Celery('online_compiler')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
