from celery import shared_task
from django.utils import timezone
from .models import SyllabusProgress, SyllabusTopic, SyllabusAuditLog
from accounts.models import CustomUser


@shared_task
def auto_generate_weekly_syllabus_reminders():
    """
    Sends weekly reminders to teachers who haven't marked syllabus progress.
    """
    pending_topics = SyllabusProgress.objects.filter(status='pending')
    notified_teachers = set()

    for progress in pending_topics:
        teacher = progress.teacher
        if teacher.id not in notified_teachers:
            # Placeholder: send_notification(teacher, ...)
            print(f"Reminder sent to {teacher.email} for pending syllabus topics.")
            notified_teachers.add(teacher.id)


@shared_task
def auto_log_uncovered_topics():
    """
    Logs all uncovered topics past estimated schedule.
    """
    today = timezone.now().date()
    uncovered_topics = SyllabusProgress.objects.filter(status='pending')

    for progress in uncovered_topics:
        topic = progress.topic
        estimated_end_date = topic.curriculum_subject.term.end_date if hasattr(topic.curriculum_subject.term, 'end_date') else None
        if estimated_end_date and estimated_end_date < today:
            SyllabusAuditLog.objects.create(
                user=progress.teacher,
                action='Uncovered Topic Alert',
                curriculum_subject=topic.curriculum_subject,
                topic=topic,
                notes=f"Topic '{topic.title}' not covered as of {today}"
            )
            print(f"Logged uncovered topic: {topic.title}")
