import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Enterprise user model with OAuth support and role-based access."""

    class Role(models.TextChoices):
        FREE = 'free', 'Free Tier'
        PREMIUM = 'premium', 'Premium'
        ENTERPRISE = 'enterprise', 'Enterprise'
        ADMIN = 'admin', 'Administrator'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.FREE)
    avatar_url = models.URLField(blank=True, default='')
    bio = models.TextField(max_length=500, blank=True, default='')

    # OAuth fields
    github_id = models.CharField(max_length=100, blank=True, default='', db_index=True)
    google_id = models.CharField(max_length=100, blank=True, default='', db_index=True)

    # Usage tracking
    executions_today = models.IntegerField(default=0)
    total_executions = models.IntegerField(default=0)
    last_execution_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['github_id']),
            models.Index(fields=['google_id']),
        ]

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def execution_limit(self):
        limits = {
            self.Role.FREE: 50,
            self.Role.PREMIUM: 500,
            self.Role.ENTERPRISE: 5000,
            self.Role.ADMIN: 99999,
        }
        return limits.get(self.role, 50)

    @property
    def can_execute(self):
        return self.executions_today < self.execution_limit


class APIKey(models.Model):
    """API keys for programmatic access."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=100)
    key_hash = models.CharField(max_length=128, unique=True)
    prefix = models.CharField(max_length=8)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_keys'

    def __str__(self):
        return f"{self.prefix}... ({self.user.email})"


class AuditLog(models.Model):
    """Security audit trail."""

    class Action(models.TextChoices):
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'
        REGISTER = 'register', 'Registration'
        PASSWORD_CHANGE = 'password_change', 'Password Change'
        OAUTH_LOGIN = 'oauth_login', 'OAuth Login'
        API_KEY_CREATE = 'api_key_create', 'API Key Created'
        CODE_EXECUTE = 'code_execute', 'Code Execution'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=Action.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action']),
        ]
