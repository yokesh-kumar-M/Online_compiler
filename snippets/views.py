import uuid
from django.db.models import F
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Snippet, ExecutionHistory, Star
from .serializers import SnippetSerializer, SnippetCreateSerializer, ExecutionHistorySerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.visibility != 'private' or obj.user == request.user
        return obj.user == request.user


class SnippetViewSet(viewsets.ModelViewSet):
    """CRUD operations for code snippets with sharing and starring."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['language', 'visibility']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'stars_count', 'views_count']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SnippetCreateSerializer
        return SnippetSerializer

    def get_queryset(self):
        qs = Snippet.objects.select_related('user')
        if self.request.user.is_authenticated:
            from django.db.models import Q
            return qs.filter(Q(visibility='public') | Q(user=self.request.user))
        return qs.filter(visibility='public')

    def perform_create(self, serializer):
        snippet = serializer.save(user=self.request.user)
        if not snippet.share_slug:
            snippet.share_slug = str(snippet.id)[:8]
            snippet.save(update_fields=['share_slug'])

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Snippet.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def star(self, request, pk=None):
        snippet = self.get_object()
        star, created = Star.objects.get_or_create(user=request.user, snippet=snippet)
        if created:
            Snippet.objects.filter(pk=snippet.pk).update(stars_count=F('stars_count') + 1)
            return Response({'status': 'starred'})
        else:
            star.delete()
            Snippet.objects.filter(pk=snippet.pk).update(stars_count=F('stars_count') - 1)
            return Response({'status': 'unstarred'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def fork(self, request, pk=None):
        original = self.get_object()
        forked = Snippet.objects.create(
            user=request.user,
            title=f"Fork of {original.title}",
            description=original.description,
            code=original.code,
            language=original.language,
            visibility='private',
            tags=original.tags,
            fork_of=original,
            share_slug=str(uuid.uuid4())[:8],
        )
        return Response(SnippetSerializer(forked, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        try:
            snippet = Snippet.objects.get(share_slug=slug)
            if snippet.visibility == 'private' and snippet.user != request.user:
                return Response({'error': 'Not found'}, status=404)
            Snippet.objects.filter(pk=snippet.pk).update(views_count=F('views_count') + 1)
            return Response(SnippetSerializer(snippet, context={'request': request}).data)
        except Snippet.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)


class ExecutionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """View execution history (read-only)."""
    serializer_class = ExecutionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExecutionHistory.objects.filter(user=self.request.user)
