from django.contrib import admin
from .models import SupportedLanguage, SystemMetrics


@admin.register(SupportedLanguage)
class SupportedLanguageAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'version', 'is_active', 'timeout_seconds', 'memory_limit_mb']
    list_filter = ['is_active']


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_executions', 'successful_executions', 'failed_executions', 'active_users_today']
    ordering = ['-date']
