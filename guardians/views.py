from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Guardian, GuardianStudentLink, GuardianNotification
from .serializers import GuardianSerializer, GuardianStudentLinkSerializer, GuardianNotificationSerializer
from .permissions import IsGuardianOrReadOnly, IsInstitutionAdmin
from institutions.models import Institution
from students.models import Student
from django.db.models import Q
from .analytics import GuardianAnalytics


class GuardianAnalyticsView(APIView):
    """
    Returns simple analytics related to guardian activity.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            guardian = Guardian.objects.get(user=user)
        except Guardian.DoesNotExist:
            return Response({"detail": "Guardian profile not found."}, status=404)

        total_students = guardian.student_links.count()
        unread_notifications = guardian.notifications.filter(is_read=False).count()
        total_notifications = guardian.notifications.count()

        data = {
            "guardian_name": user.get_full_name(),
            "linked_students": total_students,
            "total_notifications": total_notifications,
            "unread_notifications": unread_notifications,
        }
        return Response(data)

class GuardianViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.select_related('user', 'institution')
    serializer_class = GuardianSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdmin]

    def get_queryset(self):
        institution = self.request.user.institution
        return self.queryset.filter(institution=institution)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        guardian = get_object_or_404(Guardian, user=request.user)
        serializer = self.get_serializer(guardian)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request):
        institution = request.user.institution
        analytics = GuardianAnalytics(institution)
        data = analytics.generate_summary()
        return Response(data)


class GuardianStudentLinkViewSet(viewsets.ModelViewSet):
    queryset = GuardianStudentLink.objects.select_related('guardian', 'student')
    serializer_class = GuardianStudentLinkSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdmin]

    def get_queryset(self):
        institution = self.request.user.institution
        return self.queryset.filter(student__institution=institution)

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
            unread = self.queryset.filter(guardian=user.guardian, is_read=False)
            serializer = self.get_serializer(unread, many=True)
            return Response(serializer.data)
        return Response([])

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsInstitutionAdmin])
    def bulk_send(self, request):
        institution = request.user.institution
        data = request.data
        title = data.get('title')
        message = data.get('message')
        type = data.get('type', 'announcement')

        guardians = Guardian.objects.filter(institution=institution)
        notifications = [
            GuardianNotification(
                guardian=g, institution=institution, title=title,
                message=message, type=type
            ) for g in guardians
        ]
        GuardianNotification.objects.bulk_create(notifications)
        return Response({'status': 'bulk notifications sent'}, status=status.HTTP_201_CREATED)
