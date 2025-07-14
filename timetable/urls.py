from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PeriodTemplateViewSet,
    RoomViewSet,
    SubjectAssignmentViewSet,
    TimetableEntryViewSet,
)

router = DefaultRouter()
router.register(r'periods', PeriodTemplateViewSet, basename='period')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'assignments', SubjectAssignmentViewSet, basename='subject-assignment')
router.register(r'entries', TimetableEntryViewSet, basename='timetable-entry')

urlpatterns = [
    path('', include(router.urls)),

    # Named custom endpoints from TimetableEntryViewSet
    path(
        'entries/auto-generate/',
        TimetableEntryViewSet.as_view({'post': 'auto_generate'}),
        name='timetable-auto-generate'
    ),
    path(
        'entries/reschedule-absent/',
        TimetableEntryViewSet.as_view({'post': 'reschedule_absent'}),
        name='timetable-reschedule-absent'
    ),
    path(
        'entries/stream-printable/',
        TimetableEntryViewSet.as_view({'get': 'printable_by_stream'}),
        name='timetable-stream-printable'
    ),
    path(
        'entries/teacher-printable/',
        TimetableEntryViewSet.as_view({'get': 'printable_by_teacher'}),
        name='timetable-teacher-printable'
    ),
    path(
        'entries/teacher-reminders/',
        TimetableEntryViewSet.as_view({'get': 'teacher_reminders'}),
        name='timetable-teacher-reminders'
    ),
    path(
        'entries/daily-overview/',
        TimetableEntryViewSet.as_view({'get': 'teacher_overview_today'}),
        name='timetable-daily-overview'
    ),
    path(
        'entries/analytics/',
        TimetableEntryViewSet.as_view({'get': 'analytics'}),
        name='timetable-analytics'
    ),
]
