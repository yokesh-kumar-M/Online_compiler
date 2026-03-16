from rest_framework import serializers
from .models import Snippet, ExecutionHistory, Star


class SnippetSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Snippet
        fields = [
            'id', 'user', 'user_email', 'title', 'description', 'code',
            'language', 'visibility', 'share_slug', 'tags', 'fork_of',
            'stars_count', 'views_count', 'executions_count',
            'is_starred', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'stars_count', 'views_count', 'executions_count', 'created_at', 'updated_at']

    def get_is_starred(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Star.objects.filter(user=request.user, snippet=obj).exists()
        return False


class SnippetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ['title', 'description', 'code', 'language', 'visibility', 'tags']


class ExecutionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionHistory
        fields = [
            'id', 'snippet', 'code', 'language', 'status',
            'output', 'error_output', 'execution_time_ms',
            'memory_used_kb', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'output', 'error_output', 'execution_time_ms', 'memory_used_kb', 'created_at']
