from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q

from .models import (
    CommunicationAnnouncement,
    CommunicationTarget,
    CommunicationReadLog,
    CommunicationLog,
    AnnouncementCategory
)

from .serializers import (
    CommunicationAnnouncementSerializer,
    CommunicationTargetSerializer,
    CommunicationReadLogSerializer,
    CommunicationLogSerializer,
    AnnouncementCategorySerializer
)

from .permissions import IsAuthorOrAdmin
from .filters import CommunicationAnnouncementFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class AnnouncementCategoryViewSet(viewsets.ModelViewSet):
    queryset = AnnouncementCategory.objects.all()
    serializer_class = AnnouncementCategorySerializer
    permission_classes = [IsAuthenticated]


class CommunicationAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = CommunicationAnnouncement.objects.all()
    serializer_class = CommunicationAnnouncementSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CommunicationAnnouncementFilter
    search_fields = ['title', 'content', 'author__username', 'institution__name']
    ordering_fields = ['created_at', 'scheduled_at', 'expires_at']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated, IsAuthorOrAdmin]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        institution_id = getattr(user, 'institution_id', None)
        is_public = Q(is_public=True)
        is_targeted = Q(targets__user=user) | Q(targets__role=user.role) | Q(targets__class_level=user.class_level) | Q(targets__stream=user.stream)

        return CommunicationAnnouncement.objects.filter(
            Q(author=user) | is_public | is_targeted
        ).distinct()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        announcement = self.get_object()
        read_log, created = CommunicationReadLog.objects.get_or_create(
            announcement=announcement,
            user=request.user
        )
        if created:
            return Response({"detail": "Marked as read."}, status=201)
        return Response({"detail": "Already marked as read."}, status=200)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def mark_as_sent(self, request, pk=None):
        announcement = self.get_object()
        announcement.sent = True
        announcement.save(update_fields=["sent"])
        return Response({"detail": "Marked as sent."}, status=200)


class CommunicationTargetViewSet(viewsets.ModelViewSet):
    queryset = CommunicationTarget.objects.select_related('announcement', 'user', 'class_level', 'stream')
    serializer_class = CommunicationTargetSerializer
    permission_classes = [IsAuthenticated]


class CommunicationReadLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommunicationReadLog.objects.select_related('announcement', 'user')
    serializer_class = CommunicationReadLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['announcement', 'user']


class CommunicationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommunicationLog.objects.select_related('announcement')
    serializer_class = CommunicationLogSerializer
    permission_classes = [IsAuthenticated]
