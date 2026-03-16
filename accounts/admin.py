from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, APIKey, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'is_active', 'total_executions', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'avatar_url', 'bio')}),
        ('OAuth', {'fields': ('github_id', 'google_id')}),
        ('Usage', {'fields': ('executions_today', 'total_executions', 'last_execution_at')}),
    )


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['prefix', 'user', 'name', 'is_active', 'last_used_at', 'created_at']
    list_filter = ['is_active']
    search_fields = ['user__email', 'name']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['id', 'user', 'action', 'ip_address', 'user_agent', 'metadata', 'created_at']
