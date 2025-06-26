from django.shortcuts import render

from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import (
    Event, EventRSVP, EventFeedback,
    EventAttendance, EventTag, RecurringEventRule
)
from .serializers import (
    EventSerializer, EventRSVPSerializer,
    EventFeedbackSerializer, EventAttendanceSerializer,
    EventTagSerializer, RecurringEventRuleSerializer
)
from institutions.permissions import IsInstitutionMember
from .ai import suggest_slots
from accounts.models import CustomUser


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['event_type', 'is_virtual', 'start_time', 'target_roles']
    ordering_fields = ['start_time', 'created_at']
    search_fields = ['title', 'description', 'tags__name']

    def get_queryset(self):
        user = self.request.user
        institution = user.institution
        qs = Event.objects.filter(institution=institution)

        if user.role == 'student':
            qs = qs.filter(
                models.Q(target_roles__contains=['student']) |
                models.Q(target_students=user.student) |
                models.Q(target_class_levels=user.student.class_level) |
                models.Q(target_streams=user.student.stream)
            )
        elif user.role == 'guardian':
            qs = qs.filter(target_roles__contains=['guardian'])
        elif user.role == 'teacher':
            qs = qs.filter(target_roles__contains=['teacher'])
        # admins see all
        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, institution=self.request.user.institution)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        serializer = EventRSVPSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_attendance(self, request, pk=None):
        event = self.get_object()
        serializer = EventAttendanceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def feedback(self, request, pk=None):
        event = self.get_object()
        serializer = EventFeedbackSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class EventTagViewSet(viewsets.ModelViewSet):
    queryset = EventTag.objects.all()
    serializer_class = EventTagSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return EventTag.objects.all()


class RecurringEventRuleViewSet(viewsets.ModelViewSet):
    queryset = RecurringEventRule.objects.all()
    serializer_class = RecurringEventRuleSerializer
    permission_classes = [permissions.IsAuthenticated]


# ✅ AI-powered time suggestion endpoint
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def suggest_event_slots(request):
    user = request.user
    institution = user.institution
    duration = int(request.data.get('duration_minutes', 60))
    participant_ids = request.data.get('participants', [])

    participants = CustomUser.objects.filter(id__in=participant_ids)
    slots = suggest_slots(institution, duration, participants)

    return Response({"suggestions": slots})
