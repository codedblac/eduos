from celery import shared_task
from django.utils import timezone
from .models import Guardian, GuardianNotification, GuardianStudentLink
from notifications.utils import send_notification_to_user
from institutions.models import Institution
from students.models import Student


@shared_task
def send_bulk_guardian_notification(institution_id, title, message, type="announcement"):
    """
    Sends a bulk notification to all active guardians in the institution.
    """
    guardians = Guardian.objects.filter(institution_id=institution_id, is_active=True)

    for guardian in guardians:
        GuardianNotification.objects.create(
            guardian=guardian,
            institution_id=institution_id,
            title=title,
            message=message,
            type=type,
            is_read=False
        )
        send_notification_to_user(
            user=guardian.user,
            title=title,
            message=message
        )


@shared_task
def notify_guardians_of_student_status_change(student_id, status_change, extra_message=None):
    """
    Notify all linked guardians when a student's status changes (e.g., suspended, transferred).
    """
    student = Student.objects.get(id=student_id)
    links = GuardianStudentLink.objects.filter(student=student).select_related("guardian")

    title = f"Update on {student.first_name}'s Status"
    base_msg = f"{student.first_name} {student.last_name} has been {status_change.lower()}."

    message = f"{base_msg} {extra_message}" if extra_message else base_msg

    for link in links:
        GuardianNotification.objects.create(
            guardian=link.guardian,
            institution=student.institution,
            title=title,
            message=message,
            type="announcement",
            is_read=False
        )
        send_notification_to_user(
            user=link.guardian.user,
            title=title,
            message=message
        )


@shared_task
def weekly_guardian_digest():
    """
    Weekly summary of unread notifications sent to each guardian.
    This could be expanded to include student highlights, fees, performance, etc.
    """
    guardians = Guardian.objects.filter(is_active=True)

    for guardian in guardians:
        unread_count = guardian.notifications.filter(is_read=False).count()
        if unread_count > 0:
            send_notification_to_user(
                user=guardian.user,
                title="📬 Weekly Summary",
                message=f"You have {unread_count} unread notification(s) from your institution."
            )
