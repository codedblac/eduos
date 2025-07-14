from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import (
    TimetableEntry, SubjectAssignment, TimetableVersion,
    TeacherAvailabilityOverride, Room
)
from notifications.utils import send_notification_to_user
from attendance.models import ClassAttendanceRecord
from .ai import TimetableAIEngine

import logging
logger = logging.getLogger(__name__)


@shared_task
def auto_generate_timetable_for_term(institution_id, term_id):
    """
    Task: Generate a full timetable for an institution & term using AI.
    """
    logger.info(f"Generating AI timetable for institution={institution_id}, term={term_id}")
    return TimetableAIEngine.generate_timetable(institution_id=institution_id, term_id=term_id)


@shared_task
def send_daily_timetable_overview():
    """
    Task: Daily summary for each teacher at 6AM: 'Today, you have...'
    """
    now = timezone.localtime()
    weekday = now.strftime("%A")  # e.g. "Monday"

    from teachers.models import Teacher
    teachers = Teacher.objects.select_related("user")

    for teacher in teachers:
        entries = TimetableEntry.objects.filter(
            teacher=teacher,
            period_template__day=weekday
        ).select_related("subject", "stream", "period_template").order_by("period_template__start_time")

        if entries.exists():
            lessons = ', '.join([
                f"{e.subject.name} ({e.stream.name}) @ {e.period_template.start_time.strftime('%H:%M')}"
                for e in entries
            ])
            message = f"🗓 Today you have {entries.count()} lesson(s): {lessons}"
            send_notification_to_user(
                user=teacher.user,
                title="Today's Timetable",
                message=message,
                channel="in_app"
            )


@shared_task
def send_timetable_reminders():
    """
    Task: Notify teachers X minutes before each lesson starts (default 10min).
    """
    now = timezone.localtime()
    lead_minutes = 10
    window_start = (now + timedelta(minutes=lead_minutes)).time()
    window_end = (now + timedelta(minutes=lead_minutes + 1)).time()
    weekday = now.strftime("%A")

    entries = TimetableEntry.objects.filter(
        period_template__start_time__gte=window_start,
        period_template__start_time__lte=window_end,
        period_template__day=weekday
    ).select_related('teacher__user', 'subject', 'stream', 'period_template')

    for entry in entries:
        message = (
            f"⏰ You have a {entry.subject.name} lesson with {entry.stream.name} "
            f"at {entry.period_template.start_time.strftime('%H:%M')}."
        )
        send_notification_to_user(
            user=entry.teacher.user,
            title="Upcoming Lesson Reminder",
            message=message,
            channel="push"
        )


@shared_task
def auto_reschedule_absent_teachers():
    """
    Task: Check for teacher absences and reschedule today's lessons.
    """
    now = timezone.localtime()
    weekday = now.strftime("%A")

    absences = ClassAttendanceRecord.objects.filter(date=now.date(), resolved=False).select_related("teacher__user")

    for absence in absences:
        teacher = absence.teacher
        entries = TimetableEntry.objects.filter(
            teacher=teacher,
            period_template__day=weekday
        ).select_related('subject', 'stream', 'period_template')

        for entry in entries:
            substitute = TimetableAIEngine.find_substitute_teacher(
                subject=entry.subject,
                stream=entry.stream,
                period_template=entry.period_template,
                exclude_teacher=teacher
            )
            if substitute:
                logger.info(f"Substituting {teacher} with {substitute} for {entry}")
                entry.teacher = substitute
                entry.save()

                send_notification_to_user(
                    user=substitute.user,
                    title="Substitution Assignment",
                    message=(
                        f"You've been assigned to teach {entry.subject.name} for {entry.stream.name} "
                        f"at {entry.period_template.start_time.strftime('%H:%M')} "
                        f"(substituting for {teacher.user.get_full_name()})"
                    ),
                    channel="in_app"
                )

        absence.resolved = True
        absence.save()
