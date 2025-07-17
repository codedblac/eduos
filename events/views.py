from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
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
from .permissions import IsInstitutionMember
from .filters import EventFilter
from .ai import suggest_slots
from accounts.models import CustomUser


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().select_related('institution', 'created_by', 'recurring_rule')\
        .prefetch_related('tags', 'target_users', 'target_students', 'target_class_levels', 'target_streams')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = EventFilter
    ordering_fields = ['start_time', 'created_at']
    search_fields = ['title', 'description', 'tags__name']

    def get_queryset(self):
        user = self.request.user
        institution = user.institution
        qs = Event.objects.filter(institution=institution)

        if user.role == 'student' and hasattr(user, 'student'):
            student = user.student
            qs = qs.filter(
                Q(target_roles__contains=['student']) |
                Q(target_students=student) |
                Q(target_class_levels=student.class_level) |
                Q(target_streams=student.stream)
            )
        elif user.role == 'guardian':
            qs = qs.filter(Q(target_roles__contains=['guardian']))
        elif user.role == 'teacher':
            qs = qs.filter(Q(target_roles__contains=['teacher']))
        # Admins and staff see all
        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            institution=self.request.user.institution
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        serializer = EventRSVPSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_attendance(self, request, pk=None):
        event = self.get_object()
        serializer = EventAttendanceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def feedback(self, request, pk=None):
        event = self.get_object()
        serializer = EventFeedbackSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventTagViewSet(viewsets.ModelViewSet):
    queryset = EventTag.objects.all()
    serializer_class = EventTagSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return self.queryset


class RecurringEventRuleViewSet(viewsets.ModelViewSet):
    queryset = RecurringEventRule.objects.all()
    serializer_class = RecurringEventRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return self.queryset


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
