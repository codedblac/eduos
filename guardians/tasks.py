from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import GuardianNotification, Guardian
from accounts.models import CustomUser

@shared_task
def send_guardian_notification_email(notification_id):
    """
    Sends a notification email to a guardian based on the GuardianNotification instance.
    """
    try:
        notification = GuardianNotification.objects.select_related('guardian__user').get(id=notification_id)
        guardian = notification.guardian
        email = guardian.email or guardian.user.email

        if email:
            subject = f"[EduOS] {notification.title}"
            message = f"""
Dear {guardian.user.get_full_name()},

You have a new notification from {guardian.institution.name}:

Title: {notification.title}
Message: {notification.message}
Type: {notification.get_type_display()}

Regards,
EduOS System
"""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            return f"Notification email sent to {email}"
        else:
            return f"No email available for guardian {guardian}"
    except GuardianNotification.DoesNotExist:
        return f"Notification with ID {notification_id} not found."


@shared_task
def auto_expire_old_notifications(days=30):
    """
    Auto-mark notifications older than `days` as read to declutter the guardian UI.
    """
    threshold_date = timezone.now() - timezone.timedelta(days=days)
    expired = GuardianNotification.objects.filter(is_read=False, timestamp__lt=threshold_date)
    count = expired.update(is_read=True)
    return f"{count} old notifications auto-marked as read."


@shared_task
def bulk_notify_guardians(notification_type, title, message, institution_id=None):
    """
    Send a broadcast message to all guardians of an institution (or all if none is provided).
    """
    filters = {}
    if institution_id:
        filters['institution_id'] = institution_id

    guardians = Guardian.objects.filter(**filters).select_related('user', 'institution')

    notifications = [
        GuardianNotification(
            guardian=g,
            institution=g.institution,
            title=title,
            message=message,
            type=notification_type
        )
        for g in guardians
    ]
    GuardianNotification.objects.bulk_create(notifications)

    # Optionally trigger background emails (depending on scale)
    for n in notifications:
        send_guardian_notification_email.delay(n.id)

    return f"{len(notifications)} notifications sent to guardians."
