import uuid
from django.db import models
from django.conf import settings


class Snippet(models.Model):
    """Persistent code snippet with versioning and sharing."""

    class Language(models.TextChoices):
        PYTHON = 'python', 'Python'
        JAVASCRIPT = 'javascript', 'JavaScript'
        JAVA = 'java', 'Java'
        CPP = 'cpp', 'C++'
        C = 'c', 'C'
        GO = 'go', 'Go'
        RUST = 'rust', 'Rust'

    class Visibility(models.TextChoices):
        PRIVATE = 'private', 'Private'
        UNLISTED = 'unlisted', 'Unlisted'
        PUBLIC = 'public', 'Public'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='snippets')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    code = models.TextField()
    language = models.CharField(max_length=20, choices=Language.choices, default=Language.PYTHON)
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PRIVATE)
    share_slug = models.SlugField(max_length=50, unique=True, blank=True, null=True)

    # Metadata
    tags = models.JSONField(default=list, blank=True)
    fork_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='forks')
    stars_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    executions_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'snippets'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['language']),
            models.Index(fields=['visibility', '-stars_count']),
            models.Index(fields=['share_slug']),
        ]

    def __str__(self):
        return f"{self.title} ({self.language})"


class ExecutionHistory(models.Model):
    """Track code execution history."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        SUCCESS = 'success', 'Success'
        ERROR = 'error', 'Error'
        TIMEOUT = 'timeout', 'Timeout'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='executions', null=True)
    snippet = models.ForeignKey(Snippet, on_delete=models.SET_NULL, null=True, blank=True, related_name='executions')
    code = models.TextField()
    language = models.CharField(max_length=20, default='python')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    output = models.TextField(blank=True, default='')
    error_output = models.TextField(blank=True, default='')
    execution_time_ms = models.IntegerField(null=True, blank=True)
    memory_used_kb = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'execution_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]


class Star(models.Model):
    """Star/favorite a snippet."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stars')
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='stars')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stars'
        unique_together = ['user', 'snippet']
