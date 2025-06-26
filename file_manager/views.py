from django.utils import timezone
from rest_framework import viewsets, generics, permissions, filters as drf_filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import (
    ManagedFile, FileAccessLog, AssignmentSubmission
)
from .serializers import (
    ManagedFileSerializer, FileAccessLogSerializer, AssignmentSubmissionSerializer
)
from .permissions import IsUploaderOrAdmin
from .filters import ManagedFileFilter, FileAccessLogFilter
from .tasks import log_file_download


class ManagedFileViewSet(viewsets.ModelViewSet):
    queryset = ManagedFile.objects.filter(is_archived=False)
    serializer_class = ManagedFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsUploaderOrAdmin]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = ManagedFileFilter
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'version']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if not user.is_superuser:
            queryset = queryset.filter(Q(uploaded_by=user) | Q(is_public=True))
        return queryset

    def perform_destroy(self, instance):
        instance.is_archived = True
        instance.updated_at = timezone.now()
        instance.save()


class FileAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FileAccessLog.objects.select_related('user', 'file').all()
    serializer_class = FileAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_class = FileAccessLogFilter
    search_fields = ['user__username', 'file__name']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=user)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.select_related('student', 'file').all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class PublicFileListView(generics.ListAPIView):
    queryset = ManagedFile.objects.filter(is_public=True, is_archived=False)
    serializer_class = ManagedFileSerializer
    permission_classes = [permissions.AllowAny]


class MyUploadsView(generics.ListAPIView):
    serializer_class = ManagedFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ManagedFile.objects.filter(uploaded_by=self.request.user, is_archived=False)


class ExpiredFileCleanupView(generics.ListAPIView):
    """
    Admin view for inspecting expired files manually.
    Normally this cleanup is handled via Celery tasks.
    """
    serializer_class = ManagedFileSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return ManagedFile.objects.filter(expires_at__lt=timezone.now(), is_archived=False)


class RestoreFromTrashView(generics.UpdateAPIView):
    queryset = ManagedFile.objects.filter(is_archived=True)
    serializer_class = ManagedFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsUploaderOrAdmin]

    def perform_update(self, serializer):
        serializer.save(is_archived=False, updated_at=timezone.now())


class FileDownloadView(generics.RetrieveAPIView):
    queryset = ManagedFile.objects.filter(is_archived=False)
    serializer_class = ManagedFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Track download with Celery
        log_file_download.delay(file_id=instance.id, user_id=request.user.id)

        # NOTE: Download count is now tracked in FileAccessLog + FileAnalytics (not on model directly)
        return super().retrieve(request, *args, **kwargs)
