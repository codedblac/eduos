import africastalking
from django.conf import settings
from notifications.models import Notification
from django.utils import timezone
import logging


# Initialize Africa's Talking
africastalking.initialize(
    username=settings.AT_USERNAME,
    api_key=settings.AT_API_KEY
)

sms = africastalking.SMS


def send_sms(phone_number, message):
    """
    Sends SMS using Africa's Talking.
    Ensure phone_number is in international format (e.g. +2547xxxxxxx).
    """
    try:
        if phone_number.startswith('0'):
            phone_number = '+254' + phone_number[1:]
        elif not phone_number.startswith('+'):
            phone_number = '+254' + phone_number

        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return None


def send_notification_to_user(user, title, message):
    """
    Sends an in-app/system notification to a user.
    Expandable to email, push, or other channels.
    """
    from notifications.models import Notification  # adjust path if needed

    Notification.objects.create(
        recipient=user,
        title=title,
        message=message
    )


def notify_user(user, title, message, via_sms=False):
    """
    Unified interface to send notification:
    - in-app (always)
    - SMS (if via_sms=True and user has phone_number)
    """
    send_notification_to_user(user, title, message)

    if via_sms and hasattr(user, 'phone_number') and user.phone_number:
        send_sms(user.phone_number, f"{title}: {message}")


# Backward-compatible alias
send_push_notification = notify_user

logger = logging.getLogger(__name__)

def send_notification(user, title, message, category="general", institution=None, related_object=None):
    """
    Sends a notification to a user. Creates a Notification object.

    Args:
        user (User): Target user to notify.
        title (str): Title of the notification.
        message (str): Body message.
        category (str): Category (e.g., academic, system, finance, general).
        institution (Institution): Optional institution context.
        related_object (Model): Optional model instance (e.g., report, invoice) to link for deep-linking.
    """
    try:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            category=category,
            institution=institution,
            timestamp=timezone.now(),
            related_object=related_object
        )
        logger.info(f"[NOTIFICATIONS] Sent to {user}: {title}")
    except Exception as e:
        logger.exception(f"[NOTIFICATIONS] Failed to send to {user}: {e}")