from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import SyllabusProgress, SyllabusAuditLog
from notifications.utils import send_notification_to_user  # If available
from accounts.models import CustomUser
from datetime import timedelta


@shared_task(bind=True, max_retries=3)
def auto_generate_weekly_syllabus_reminders(self):
    """
    Sends weekly reminders to teachers with pending syllabus topics.
    """
    pending_progress_qs = SyllabusProgress.objects.filter(status='pending')
    notified_teachers = set()

    for progress in pending_progress_qs.select_related('teacher', 'topic'):
        teacher = progress.teacher
        if teacher and teacher.id not in notified_teachers:
            notified_teachers.add(teacher.id)

            try:
                # Optional: actual notification mechanism
                send_notification_to_user(
                    user=teacher,
                    title="Pending Syllabus Topics",
                    message="You have pending syllabus topics not yet marked as 'covered'. Please update your progress."
                )
                print(f"Reminder sent to {teacher.email} for pending syllabus topics.")
            except Exception as e:
                print(f"Failed to notify {teacher.email}: {e}")


@shared_task(bind=True, max_retries=3)
def auto_log_uncovered_topics(self):
    """
    Automatically logs all syllabus topics that were not covered
    before their estimated term end.
    """
    today = timezone.now().date()

    pending_progress = SyllabusProgress.objects.filter(status='pending').select_related(
        'topic', 'teacher', 'topic__curriculum_subject__term'
    )

    for progress in pending_progress:
        topic = progress.topic
        term = topic.curriculum_subject.term
        estimated_end = getattr(term, 'end_date', None)

        if estimated_end and estimated_end < today:
            # Avoid duplicate log entries
            already_logged = SyllabusAuditLog.objects.filter(
                topic=topic,
                user=progress.teacher,
                action='Uncovered Topic Alert'
            ).exists()

            if not already_logged:
                SyllabusAuditLog.objects.create(
                    user=progress.teacher,
                    action='Uncovered Topic Alert',
                    curriculum_subject=topic.curriculum_subject,
                    topic=topic,
                    notes=f"Topic '{topic.title}' remains uncovered after term end ({estimated_end})."
                )
                print(f"[Logged] Uncovered topic: {topic.title} by {progress.teacher}")


@shared_task
def auto_escalate_long_pending_topics(threshold_days=14):
    """
    Identify syllabus topics marked pending for longer than `threshold_days`,
    and notify both teacher and admin (optional future escalation).
    """
    cutoff = timezone.now() - timedelta(days=threshold_days)
    stale_progress = SyllabusProgress.objects.filter(
        status='pending',
        coverage_date__isnull=True,
        topic__created_at__lt=cutoff
    ).select_related('teacher')

    for progress in stale_progress:
        teacher = progress.teacher
        try:
            send_notification_to_user(
                user=teacher,
                title="Stalled Syllabus Progress",
                message=f"The topic '{progress.topic.title}' has been pending for over {threshold_days} days."
            )
        except Exception as e:
            print(f"Failed to escalate topic to {teacher}: {e}")
