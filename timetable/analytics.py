from datetime import timedelta
from django.db.models import Count, Q, F
from django.utils.timezone import now

from .models import (
    TimetableEntry, SubjectAssignment, PeriodTemplate,
    Room, Stream, Teacher
)


class TimetableAnalyticsEngine:

    @staticmethod
    def weekly_subject_distribution(institution):
        """Count how many lessons each subject has per stream."""
        data = TimetableEntry.objects.filter(version__institution=institution)
        results = data.values(
            stream_name=F('stream__name'),
            subject_name=F('subject__name')
        ).annotate(total=Count('id')).order_by('stream_name', 'subject_name')
        return list(results)

    @staticmethod
    def teacher_workload(institution):
        """Total lessons each teacher is teaching per week."""
        data = TimetableEntry.objects.filter(version__institution=institution)
        results = data.values(
            teacher_name=F('teacher__user__first_name')  # Or custom method if `get_full_name` is used
        ).annotate(total=Count('id')).order_by('-total')
        return list(results)

    @staticmethod
    def period_utilization(institution):
        """How often each period slot is used."""
        data = TimetableEntry.objects.filter(version__institution=institution)
        results = data.values(
            day=F('period_template__day'),
            start_time=F('period_template__start_time'),
            end_time=F('period_template__end_time')
        ).annotate(usage_count=Count('id')).order_by('day', 'start_time')
        return list(results)

    @staticmethod
    def room_utilization(institution):
        """How often each room is used."""
        data = TimetableEntry.objects.filter(version__institution=institution).exclude(room=None)
        results = data.values(
            room_name=F('room__name')
        ).annotate(usage_count=Count('id')).order_by('-usage_count')
        return list(results)

    @staticmethod
    def stream_coverage(institution):
        """Total lessons per stream per week."""
        data = TimetableEntry.objects.filter(version__institution=institution)
        results = data.values(
            stream_name=F('stream__name')
        ).annotate(total_lessons=Count('id')).order_by('-total_lessons')
        return list(results)

    @staticmethod
    def detect_conflicts(institution):
        """Detect scheduling conflicts by teacher, room, or stream."""
        conflicts = []
        entries = TimetableEntry.objects.filter(version__institution=institution)

        # Conflict by teacher
        teacher_conflicts = entries.values('teacher', 'period_template').annotate(total=Count('id')).filter(total__gt=1)
        for conflict in teacher_conflicts:
            conflicts.append({
                'type': 'Teacher Conflict',
                'teacher_id': conflict['teacher'],
                'period_template_id': conflict['period_template'],
                'instances': conflict['total']
            })

        # Conflict by room
        room_conflicts = entries.exclude(room=None).values('room', 'period_template').annotate(total=Count('id')).filter(total__gt=1)
        for conflict in room_conflicts:
            conflicts.append({
                'type': 'Room Conflict',
                'room_id': conflict['room'],
                'period_template_id': conflict['period_template'],
                'instances': conflict['total']
            })

        # Conflict by stream
        stream_conflicts = entries.values('stream', 'period_template').annotate(total=Count('id')).filter(total__gt=1)
        for conflict in stream_conflicts:
            conflicts.append({
                'type': 'Stream Conflict',
                'stream_id': conflict['stream'],
                'period_template_id': conflict['period_template'],
                'instances': conflict['total']
            })

        return conflicts

    @staticmethod
    def under_or_over_scheduled_streams(institution, lower_limit=25, upper_limit=40):
        """Streams with too few or too many weekly lessons."""
        data = TimetableEntry.objects.filter(version__institution=institution)
        grouped = data.values('stream__name').annotate(total=Count('id')).order_by('stream__name')

        alerts = []
        for entry in grouped:
            if entry['total'] < lower_limit:
                alerts.append({
                    'stream': entry['stream__name'],
                    'issue': 'Under-scheduled',
                    'lessons': entry['total']
                })
            elif entry['total'] > upper_limit:
                alerts.append({
                    'stream': entry['stream__name'],
                    'issue': 'Over-scheduled',
                    'lessons': entry['total']
                })

        return alerts

    @staticmethod
    def audit_summary(institution):
        """Dashboard overview stats."""
        return {
            'total_timetable_entries': TimetableEntry.objects.filter(version__institution=institution).count(),
            'active_teachers': Teacher.objects.filter(assignments__institution=institution).distinct().count(),
            'active_rooms': Room.objects.filter(timetable_entries__version__institution=institution).distinct().count(),
            'streams_scheduled': Stream.objects.filter(timetable_entries__version__institution=institution).distinct().count(),
        }
