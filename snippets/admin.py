from django.contrib import admin
from .models import Snippet, ExecutionHistory, Star


@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'language', 'visibility', 'stars_count', 'views_count', 'created_at']
    list_filter = ['language', 'visibility', 'created_at']
    search_fields = ['title', 'description', 'user__email']


@admin.register(ExecutionHistory)
class ExecutionHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'language', 'status', 'execution_time_ms', 'created_at']
    list_filter = ['status', 'language', 'created_at']


@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ['user', 'snippet', 'created_at']
