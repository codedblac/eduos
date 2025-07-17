from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Guardian, GuardianStudentLink, GuardianNotification
from .serializers import (
    GuardianSerializer,
    GuardianStudentLinkSerializer,
    GuardianNotificationSerializer,
)
from .permissions import IsGuardianOrReadOnly, IsInstitutionAdminOrStaff
from .analytics import GuardianAnalytics
from .ai import GuardianAIEngine


class GuardianViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.select_related('user', 'institution')
    serializer_class = GuardianSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrStaff]

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        guardian = get_object_or_404(Guardian, user=request.user)
        serializer = self.get_serializer(guardian)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def ai_summary(self, request):
        guardian = get_object_or_404(Guardian, user=request.user)
        engine = GuardianAIEngine(guardian)
        data = engine.run_analysis()
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsInstitutionAdminOrStaff])
    def analytics(self, request):
        analytics = GuardianAnalytics(institution=request.user.institution)
        return Response(analytics.generate_summary())


class GuardianStudentLinkViewSet(viewsets.ModelViewSet):
    queryset = GuardianStudentLink.objects.select_related('guardian', 'student')
    serializer_class = GuardianStudentLinkSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrStaff]

    def get_queryset(self):
        return self.queryset.filter(student__institution=self.request.user.institution)

    def perform_create(self, serializer):
        guardian = serializer.validated_data['guardian']
        student = serializer.validated_data['student']
        if guardian.institution != student.institution:
            raise serializers.ValidationError("Guardian and student must belong to the same institution.")
        serializer.save()


class GuardianNotificationViewSet(viewsets.ModelViewSet):
    queryset = GuardianNotification.objects.select_related('guardian', 'institution')
    serializer_class = GuardianNotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsGuardianOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'guardian'):
            return self.queryset.filter(guardian=user.guardian)
        return self.queryset.none()

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'status': 'marked as read'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        user = request.user
        if hasattr(user, 'guardian'):
            unread_qs = self.get_queryset().filter(is_read=False)
            serializer = self.get_serializer(unread_qs, many=True)
            return Response(serializer.data)
        return Response([])

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsInstitutionAdminOrStaff])
    def bulk_send(self, request):
        institution = request.user.institution
        title = request.data.get('title')
        message = request.data.get('message')
        type = request.data.get('type', 'announcement')

        if not title or not message:
            return Response({'detail': 'Title and message are required.'}, status=400)

        guardians = Guardian.objects.filter(institution=institution)
        notifications = [
            GuardianNotification(
                guardian=g,
                institution=institution,
                title=title,
                message=message,
                type=type
            ) for g in guardians
        ]
        GuardianNotification.objects.bulk_create(notifications)
        return Response({'status': 'Bulk notifications sent.'}, status=status.HTTP_201_CREATED)


class GuardianAnalyticsView(APIView):
    """
    Lightweight self-service analytics for a single guardian.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            guardian = Guardian.objects.get(user=request.user)
        except Guardian.DoesNotExist:
            return Response({"detail": "Guardian profile not found."}, status=404)

        engine = GuardianAIEngine(guardian)
        data = engine.run_analysis()
        return Response(data)
