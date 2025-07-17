from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    SchoolAttendanceRecord,
    ClassAttendanceRecord,
    AbsenceReason
)
from .serializers import (
    SchoolAttendanceSerializer,
    ClassAttendanceSerializer,
    AbsenceReasonSerializer
)
from .filters import (
    SchoolAttendanceFilter,
    ClassAttendanceFilter,
    
)
from .analytics import AttendanceAnalytics


class BaseInstitutionViewSet(viewsets.ModelViewSet):
    """
    Enforces institution filtering and assignment for all attendance views.
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(
            institution=self.request.user.institution,
            recorded_by=self.request.user
        )


class SchoolAttendanceViewSet(BaseInstitutionViewSet):
    queryset = SchoolAttendanceRecord.objects.select_related('user', 'recorded_by').all().order_by('-date')
    serializer_class = SchoolAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = SchoolAttendanceFilter
    search_fields = ['user__full_name']
    ordering_fields = ['date', 'entry_time', 'exit_time']

    @action(detail=False, methods=['get'], url_path='daily-summary')
    def daily_summary(self, request):
        analytics = AttendanceAnalytics(institution=request.user.institution)
        summary = analytics.daily_school_summary()
        return Response(summary)

    @action(detail=False, methods=['get'], url_path='late-arrivals')
    def late_arrivals(self, request):
        analytics = AttendanceAnalytics(institution=request.user.institution)
        summary = analytics.late_arrivals_summary()
        return Response(summary)


class ClassAttendanceViewSet(BaseInstitutionViewSet):
    queryset = ClassAttendanceRecord.objects.select_related(
        'student', 'teacher', 'subject', 'class_level', 'stream', 'timetable_entry'
    ).all().order_by('-date')
    serializer_class = ClassAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ClassAttendanceFilter
    search_fields = ['student__full_name', 'teacher__full_name', 'subject__name']
    ordering_fields = ['date', 'status']

    @action(detail=False, methods=['get'], url_path='top-absentees')
    def top_absentees(self, request):
        analytics = AttendanceAnalytics(institution=request.user.institution)
        data = analytics.top_absentees()
        return Response(data)

    @action(detail=False, methods=['get'], url_path='teacher-absences')
    def teacher_missed_lessons(self, request):
        analytics = AttendanceAnalytics(institution=request.user.institution)
        data = analytics.teacher_missed_lessons()
        return Response(data)

    @action(detail=False, methods=['get'], url_path='absence-trend')
    def absence_trend(self, request):
        analytics = AttendanceAnalytics(institution=request.user.institution)
        data = analytics.weekly_absence_trend()
        return Response(data)


class AbsenceReasonViewSet(BaseInstitutionViewSet):
    queryset = AbsenceReason.objects.all()
    serializer_class = AbsenceReasonSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['reason']
