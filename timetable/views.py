from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from classes.models import Stream, ClassLevel
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from .models import (
    Room, SubjectAssignment, TimetableEntry,
    TimetableVersion, PeriodTemplate
)
from .serializers import (
    RoomSerializer, SubjectAssignmentSerializer, TimetableEntrySerializer,
    TimetableVersionSerializer, PeriodTemplateSerializer
)
from .filters import (
    RoomFilter, SubjectAssignmentFilter, TimetableEntryFilter,
    PeriodTemplateFilter
)
from .permissions import IsInstitutionAdminOrReadOnly
from .ai import TimetableAIEngine
from .analytics import TimetableAnalyticsEngine
from .pdf_generator import generate_teacher_timetable_pdf, generate_stream_timetable_pdf


class PeriodTemplateViewSet(viewsets.ModelViewSet):
    queryset = PeriodTemplate.objects.all()
    serializer_class = PeriodTemplateSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PeriodTemplateFilter
    search_fields = ['day', 'class_level__name', 'institution__name']


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RoomFilter
    search_fields = [ 'institution__name']


class SubjectAssignmentViewSet(viewsets.ModelViewSet):
    queryset = SubjectAssignment.objects.all()
    serializer_class = SubjectAssignmentSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SubjectAssignmentFilter
    search_fields = [
        'teacher__user__first_name',
        'teacher__user__last_name',
        'subject__name',
        'stream__name'
    ]


class TimetableEntryViewSet(viewsets.ModelViewSet):
    queryset = TimetableEntry.objects.all()
    serializer_class = TimetableEntrySerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TimetableEntryFilter
    search_fields = ['subject__name', 'teacher__user__first_name', 'stream__name']

    @action(detail=False, methods=['post'], url_path='auto-generate')
    def auto_generate(self, request):
        institution_id = request.data.get("institution_id")
        term_id = request.data.get("term_id")
        if not institution_id or not term_id:
            return Response({"error": "institution_id and term_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        TimetableAIEngine.generate_timetable_for_term(institution_id, term_id)
        return Response({"message": "Timetable generation started."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='reschedule-absent')
    def reschedule_absent(self, request):
        teacher_id = request.data.get("teacher_id")
        date = request.data.get("date")
        institution_id = request.data.get("institution_id")
        if not teacher_id or not date or not institution_id:
            return Response({"error": "teacher_id, date, and institution_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        TimetableAIEngine.reschedule_absent_teacher(teacher_id, date, institution_id)
        return Response({"message": "Rescheduling complete."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='stream-printable')
    def printable_by_stream(self, request):
        stream_id = request.query_params.get("stream_id")
        if not stream_id:
            return Response({"error": "stream_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        stream = get_object_or_404(Stream, pk=stream_id)
        return generate_stream_timetable_pdf(stream)

    @action(detail=False, methods=['get'], url_path='teacher-printable')
    def printable_by_teacher(self, request):
        teacher = getattr(request.user, 'teacher', None)
        if not teacher:
            return Response({"error": "Only teachers can access this route"}, status=status.HTTP_403_FORBIDDEN)
        return generate_teacher_timetable_pdf(teacher)

    @action(detail=False, methods=['get'], url_path='teacher-reminders')
    def teacher_reminders(self, request):
        teacher = getattr(request.user, 'teacher', None)
        if not teacher:
            return Response({"error": "Not a teacher account"}, status=status.HTTP_403_FORBIDDEN)
        buffer = int(request.query_params.get('lead_time', 10))
        reminders = TimetableAIEngine.auto_notify_teachers_upcoming_lessons(buffer_minutes=buffer)
        return Response(reminders, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='daily-overview')
    def teacher_overview_today(self, request):
        teacher = getattr(request.user, 'teacher', None)
        if not teacher:
            return Response({"error": "Not a teacher account"}, status=status.HTTP_403_FORBIDDEN)
        overview = TimetableAIEngine.today_summary_for_teacher(teacher)
        return Response(overview, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        institution_id = request.query_params.get("institution_id")
        if not institution_id:
            return Response({"error": "institution_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        analytics = TimetableAnalyticsEngine.audit_summary(institution_id)
        return Response(analytics, status=status.HTTP_200_OK)
