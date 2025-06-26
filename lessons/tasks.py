from celery import shared_task
from django.utils import timezone
from lessons.models import LessonSchedule, LessonSession
from syllabus.models import SyllabusTopic
from django.db.models import Q
from datetime import timedelta
from notifications.utils import notify_user


@shared_task
def auto_mark_missed_lessons():
    """
    Auto-mark lessons as 'missed' if their scheduled date/time has passed and no session was recorded.
    """
    now = timezone.now()
    missed = LessonSchedule.objects.filter(
        scheduled_date__lt=now.date(),
        session__isnull=True,
        status='scheduled'
    )
    for lesson in missed:
        lesson.status = 'missed'
        lesson.save()
        notify_user(lesson.lesson_plan.teacher, f"You missed a scheduled lesson on {lesson.scheduled_date}.")


@shared_task
def weekly_syllabus_progress_alert():
    """
    Weekly task to notify teachers if their syllabus progress is lagging.
    """
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    teachers = set()

    for topic in SyllabusTopic.objects.all():
        plans = topic.lessonplan_set.all()
        for plan in plans:
            total_sessions = plan.schedules.count()
            delivered_sessions = plan.schedules.filter(session__isnull=False).count()
            if total_sessions > 0 and delivered_sessions / total_sessions < 0.5:
                teachers.add(plan.teacher)

    for teacher in teachers:
        notify_user(teacher, "Your lesson coverage this week is below 50%. Please review your plans.")


@shared_task
def suggest_next_week_lessons():
    """
    Suggest lesson plans for the upcoming week based on syllabus and past sessions.
    """
    from .ai import generate_lesson_plan_suggestions
    generate_lesson_plan_suggestions()
