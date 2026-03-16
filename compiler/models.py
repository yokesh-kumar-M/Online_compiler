from django.db import models
from django.conf import settings
import uuid


class SupportedLanguage(models.Model):
    """Languages supported by the compiler platform."""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    file_extension = models.CharField(max_length=10)
    docker_image = models.CharField(max_length=200, blank=True, default='')
    is_active = models.BooleanField(default=True)
    timeout_seconds = models.IntegerField(default=10)
    memory_limit_mb = models.IntegerField(default=128)
    template_code = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'supported_languages'
        ordering = ['display_name']

    def __str__(self):
        return f"{self.display_name} ({self.version})"


class SystemMetrics(models.Model):
    """System-level metrics for monitoring."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_executions = models.BigIntegerField(default=0)
    successful_executions = models.BigIntegerField(default=0)
    failed_executions = models.BigIntegerField(default=0)
    average_execution_time_ms = models.FloatField(default=0)
    active_users_today = models.IntegerField(default=0)
    date = models.DateField(unique=True)

    class Meta:
        db_table = 'system_metrics'
        ordering = ['-date']
