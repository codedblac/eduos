from celery import shared_task
from django.utils import timezone
from teachers.models import Teacher
from notifications.utils import send_notification_to_user
from .ai import TeacherAIEngine


@shared_task
def run_teacher_ai_analysis(institution_id):
    """
    Runs AI analysis for all active teachers in an institution.
    Updates insights, performance score, and recommended subjects.
    """
    teachers = Teacher.objects.filter(institution_id=institution_id, is_active=True)

    for teacher in teachers:
        try:
            ai_engine = TeacherAIEngine(teacher)
            summary = ai_engine.generate_insight_summary()

            teacher.performance_score = summary.get("performance_score")
            teacher.ai_insights = "\n".join(summary.get("insights", []))
            teacher.recommended_subjects = summary.get("recommendations", [])
            teacher.student_feedback_summary = summary.get("feedback_summary", "")
            teacher.save(update_fields = [
                "performance_score",
                "ai_insights",
                "recommended_subjects",
                "student_feedback_summary"
            ])
        except Exception as e:
            print(f"[AI ERROR] Failed to analyze {teacher}: {str(e)}")


@shared_task
def notify_teachers_new_timetable():
    """
    Notify teachers whose timetable was updated in the last 24 hours.
    """
    updated_since = timezone.now() - timezone.timedelta(hours=24)
    teachers = Teacher.objects.filter(timetable_pdf__isnull=False, updated_at__gte=updated_since)

    for teacher in teachers:
        if teacher.user:
            send_notification_to_user(
                user=teacher.user,
                title="New Timetable Available",
                message="Your updated teaching timetable has been published. Please review it in the portal."
            )


@shared_task
def flag_inactive_teachers(days=60):
    """
    Flags and deactivates teachers not seen in the system for `days` days.
    Notifies institution admins of the status change.
    """
    cutoff = timezone.now().date() - timezone.timedelta(days=days)
    inactive_teachers = Teacher.objects.filter(is_active=True, updated_at__lt=cutoff)

    for teacher in inactive_teachers:
        teacher.is_active = False
        teacher.save(update_fields = ["is_active"])

        admins = teacher.institution.customuser_set.filter(is_staff=True)
        for admin in admins:
            send_notification_to_user(
                user=admin,
                title="Teacher Deactivated Due to Inactivity",
                message=f"{teacher.full_name} has been auto-deactivated after {days} days of inactivity."
            )
