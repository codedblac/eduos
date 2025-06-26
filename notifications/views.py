from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import (
    Notification,
    NotificationDelivery,
    NotificationPreference
)
from .serializers import (
    NotificationSerializer,
    NotificationDeliverySerializer,
    NotificationPreferenceSerializer
)
from accounts.models import CustomUser as User
from students.models import Student


class BaseInstitutionViewSet(viewsets.ModelViewSet):
    """Reusable base viewset enforcing institution-level scoping"""
    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(
            institution=self.request.user.institution,
            created_by=self.request.user
        )


class NotificationViewSet(BaseInstitutionViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Teachers, students, guardians, admins only see their own institution's notifications
        return qs.filter(
            Q(target_users=user) |
            Q(target_roles__icontains=user.role) |
            Q(target_class_levels__in=getattr(user, 'classes', [])) |
            Q(target_streams__in=getattr(user, 'streams', [])) |
            Q(target_students__in=Student.objects.filter(user=user)) |
            Q(target_roles=None, target_users=None)  # general broadcast
        ).distinct()


class NotificationDeliveryViewSet(viewsets.ModelViewSet):
    queryset = NotificationDelivery.objects.all()
    serializer_class = NotificationDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationDelivery.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        delivery = self.get_object()
        delivery.read = True
        delivery.read_at = timezone.now()
        delivery.save()
        return Response({'detail': 'Marked as read'}, status=200)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
