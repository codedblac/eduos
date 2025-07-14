# timetable/ai.py
from .models import (
    TimetableEntry, PeriodTemplate, SubjectAssignment, Stream,
    Room, TimetableVersion
)
from .models import TimetableEntry,  SubjectAssignment, Stream, Room
from teachers.models import Teacher
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone

class TimetableAIEngine:

    @staticmethod
    def generate_timetable_for_institution(institution):
        """
        Core AI function to auto-generate a timetable for an institution.
        Clears previous entries and auto-assigns teachers/subjects based on SubjectAssignments.
        """
        TimetableEntry.objects.filter(institution=institution).delete()

        assignments = SubjectAssignment.objects.filter(institution=institution)
        periods = PeriodTemplate.objects.filter(institution=institution).order_by('day', 'start_time')
        streams = Stream.objects.filter(institution=institution)

        period_index = 0
        total_periods = periods.count()

        for assignment in assignments:
            lesson_count = assignment.lessons_per_week
            assigned = 0

            while assigned < lesson_count and period_index < total_periods:
                period = periods[period_index % total_periods]

                # Check for conflicts (teacher or stream already booked)
                conflict = TimetableEntry.objects.filter(
                    Q(period=period),
                    Q(stream=assignment.stream) | Q(teacher=assignment.teacher),
                    institution=institution
                ).exists()

                if not conflict:
                    TimetableEntry.objects.create(
                        period=period,
                        stream=assignment.stream,
                        subject=assignment.subject,
                        teacher=assignment.teacher,
                        room=None,
                        institution=institution
                    )
                    assigned += 1

                period_index += 1

    @staticmethod
    def reschedule_absent_teacher(absent_teacher, date, institution):
        """
        Automatically reassigns lessons for an absent teacher to other qualified teachers
        who are free at the same period and mapped to the same stream/subject.
        """
        entries = TimetableEntry.objects.filter(
            teacher=absent_teacher,
            period__day=date.strftime('%a').upper()[:3],
            institution=institution
        )

        for entry in entries:
            # Get all teachers who teach the same subject in this institution
            qualified_teachers = Teacher.objects.filter(
                subject_links__subject=entry.subject,
                subject_links__stream=entry.stream
            ).exclude(id=absent_teacher.id)

            for teacher in qualified_teachers:
                conflict = TimetableEntry.objects.filter(
                    period=entry.period,
                    teacher=teacher,
                    institution=institution
                ).exists()

                if not conflict:
                    entry.teacher = teacher
                    entry.save()
                    break

    @staticmethod
    def suggest_best_periods_for_stream(stream, subject, teacher, institution):
        """
        AI suggests best available periods for assigning a new lesson without conflict.
        """
        suggestions = []
        all_periods = PeriodTemplate.objects.filter(institution=institution).order_by('day', 'start_time')

        for period in all_periods:
            has_conflict = TimetableEntry.objects.filter(
                period=period,
                institution=institution
            ).filter(
                Q(stream=stream) | Q(teacher=teacher)
            ).exists()

            if not has_conflict:
                suggestions.append(period)

        return suggestions

    @staticmethod
    def auto_notify_teachers_upcoming_lessons(buffer_minutes=10):
        """
        Notify teachers with lessons starting within the buffer (default 10 minutes).
        """
        now = timezone.now()
        upcoming_periods = PeriodTemplate.objects.filter(
            start_time__gte=(now + timedelta(minutes=buffer_minutes)).time(),
            start_time__lte=(now + timedelta(minutes=buffer_minutes + 5)).time()
        )

        notifications = []
        for period in upcoming_periods:
            today_day = now.strftime('%a').upper()[:3]
            entries = TimetableEntry.objects.filter(
                period__day=today_day,
                period__start_time=period.start_time,
            )

            for entry in entries:
                notifications.append({
                    'teacher_id': entry.teacher.id,
                    'message': f"Reminder: You have {entry.subject.name} with {entry.stream.name} at {entry.period.start_time.strftime('%H:%M')}"
                })

        return notifications

    @staticmethod
    def today_summary_for_teacher(teacher):
        """
        Daily lesson overview for a specific teacher.
        """
        today = timezone.now().strftime('%a').upper()[:3]
        lessons = TimetableEntry.objects.filter(
            teacher=teacher,
            period__day=today
        ).order_by('period__start_time')

        return [
            f"{entry.subject.name} ({entry.stream.name}) at {entry.period.start_time.strftime('%H:%M')}"
            for entry in lessons
        ]
