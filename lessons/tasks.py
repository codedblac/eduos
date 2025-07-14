# lessons/tasks.py

from celery import shared_task
from django.utils import timezone
from .models import LessonPlan, LessonSchedule, LessonSession
from notifications.utils import notify_user
from accounts.models import CustomUser
from datetime import timedelta

from .ai import LessonPlannerAI


@shared_task
def send_upcoming_lesson_notifications():
    """
    Notify teachers about upcoming lessons scheduled for the next day.
    """
    tomorrow = timezone.now().date() + timedelta(days=1)
    schedules = LessonSchedule.objects.filter(scheduled_date=tomorrow, status='scheduled')

    for schedule in schedules:
        teacher = schedule.lesson_plan.teacher
        if teacher:
            notify_user(
                user=teacher,
                title="Upcoming Lesson Reminder",
                message=f"You have a lesson scheduled for {schedule.scheduled_date} at {schedule.scheduled_time}.",
                source_app='lessons'
            )


@shared_task
def flag_unreviewed_lessons():
    """
    Identify lesson sessions that are more than 3 days old and still not reviewed.
    """
    cutoff = timezone.now() - timedelta(days=3)
    unreviewed = LessonSession.objects.filter(delivered_on__lte=cutoff.date(), is_reviewed=False)

    for session in unreviewed:
        notify_user(
            user=session.recorded_by,
            title="Unreviewed Lesson Alert",
            message=f"Your lesson on {session.delivered_on} for {session.lesson_schedule.lesson_plan.subject.name} is still pending review.",
            source_app='lessons'
        )


@shared_task
def auto_generate_lesson_plan_suggestions():
    """
    Run AI suggestions across all teachers who haven't planned lessons for the current week.
    """
    today = timezone.now().date()
    current_week = today.isocalendar()[1]

    # Get all active teachers
    teachers = CustomUser.objects.filter(is_teacher=True)

    for teacher in teachers:
        if not LessonPlan.objects.filter(
            teacher=teacher,
            week_number=current_week,
            term__is_active=True
        ).exists():
            # Generate suggestions
            suggestions = LessonPlannerAI.suggest_plans_for_teacher(teacher.id, current_week)
            if suggestions:
                notify_user(
                    user=teacher,
                    title="Lesson Planning Suggestions Ready",
                    message="We've generated AI-based lesson suggestions for this week. Review and customize them in the planner.",
                    source_app='lessons'
                )


@shared_task
def analyze_coverage_gaps():
    """
    Periodic check to analyze which classes or subjects are falling behind in lesson coverage.
    Sends alerts to teachers/HODs.
    """
    flagged = LessonPlannerAI.flag_low_coverage_subjects()

    for entry in flagged:
        teacher = entry.get("teacher")
        subject = entry.get("subject")
        class_level = entry.get("class_level")

        notify_user(
            user=teacher,
            title="Lesson Coverage Alert",
            message=f"Coverage is below expected for {subject.name} - {class_level.name}. Please review and update lesson sessions.",
            source_app='lessons'
        )
