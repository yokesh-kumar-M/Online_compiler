import logging
import requests
from django.conf import settings
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import User, AuditLog
from .serializers import (
    RegisterSerializer, LoginSerializer,
    UserSerializer, ChangePasswordSerializer,
)

logger = logging.getLogger('accounts')


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded.split(',')[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR')


def _log_audit(user, action, request, metadata=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        ip_address=_get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        metadata=metadata or {},
    )


def _get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


class RegisterView(generics.CreateAPIView):
    """Register a new user account."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _log_audit(user, AuditLog.Action.REGISTER, request)
        tokens = _get_tokens(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'message': 'Registration successful.',
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate and receive JWT tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        _log_audit(user, AuditLog.Action.LOGIN, request)
        tokens = _get_tokens(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
        })


class LogoutView(APIView):
    """Blacklist refresh token on logout."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            _log_audit(request.user, AuditLog.Action.LOGOUT, request)
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'message': 'Logged out.'})


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change user password."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        _log_audit(request.user, AuditLog.Action.PASSWORD_CHANGE, request)
        return Response({'message': 'Password changed successfully.'})


class GitHubOAuthView(APIView):
    """Handle GitHub OAuth 2.0 callback."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Authorization code required.'}, status=400)

        try:
            # Exchange code for access token
            token_response = requests.post(
                'https://github.com/login/oauth/access_token',
                data={
                    'client_id': settings.GITHUB_CLIENT_ID,
                    'client_secret': settings.GITHUB_CLIENT_SECRET,
                    'code': code,
                    'redirect_uri': settings.GITHUB_REDIRECT_URI,
                },
                headers={'Accept': 'application/json'},
                timeout=10,
            )
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            if not access_token:
                return Response({'error': 'Failed to obtain access token.'}, status=400)

            # Get user info
            user_response = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10,
            )
            github_user = user_response.json()

            # Get email
            email = github_user.get('email')
            if not email:
                emails_response = requests.get(
                    'https://api.github.com/user/emails',
                    headers={'Authorization': f'Bearer {access_token}'},
                    timeout=10,
                )
                emails = emails_response.json()
                primary = next((e for e in emails if e.get('primary')), None)
                email = primary['email'] if primary else emails[0]['email']

            github_id = str(github_user['id'])

            # Find or create user
            user = User.objects.filter(github_id=github_id).first()
            if not user:
                user = User.objects.filter(email=email).first()
                if user:
                    user.github_id = github_id
                    user.save()
                else:
                    user = User.objects.create_user(
                        email=email,
                        username=github_user.get('login', email.split('@')[0]),
                        github_id=github_id,
                        avatar_url=github_user.get('avatar_url', ''),
                        first_name=github_user.get('name', '').split(' ')[0] if github_user.get('name') else '',
                        password=None,
                    )

            _log_audit(user, AuditLog.Action.OAUTH_LOGIN, request, {'provider': 'github'})
            tokens = _get_tokens(user)

            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens,
            })

        except requests.RequestException as e:
            logger.error(f'GitHub OAuth error: {e}')
            return Response({'error': 'GitHub authentication failed.'}, status=500)


class GoogleOAuthView(APIView):
    """Handle Google OAuth 2.0 callback."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Authorization code required.'}, status=400)

        try:
            token_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': settings.GOOGLE_CLIENT_ID,
                    'client_secret': settings.GOOGLE_CLIENT_SECRET,
                    'code': code,
                    'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                    'grant_type': 'authorization_code',
                },
                timeout=10,
            )
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            if not access_token:
                return Response({'error': 'Failed to obtain access token.'}, status=400)

            user_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10,
            )
            google_user = user_response.json()
            google_id = google_user['id']
            email = google_user['email']

            user = User.objects.filter(google_id=google_id).first()
            if not user:
                user = User.objects.filter(email=email).first()
                if user:
                    user.google_id = google_id
                    user.save()
                else:
                    user = User.objects.create_user(
                        email=email,
                        username=email.split('@')[0],
                        google_id=google_id,
                        avatar_url=google_user.get('picture', ''),
                        first_name=google_user.get('given_name', ''),
                        last_name=google_user.get('family_name', ''),
                        password=None,
                    )

            _log_audit(user, AuditLog.Action.OAUTH_LOGIN, request, {'provider': 'google'})
            tokens = _get_tokens(user)

            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens,
            })

        except requests.RequestException as e:
            logger.error(f'Google OAuth error: {e}')
            return Response({'error': 'Google authentication failed.'}, status=500)
