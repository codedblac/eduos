# accounts/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import CustomUser
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_welcome_email_task(user_id):
    """
    Send welcome email after user account creation.
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
        subject = "Welcome to EduOS"
        message = f"""
        Hello {user.first_name},

        Welcome to EduOS — your school and learning platform.

        You can now log in using your email: {user.email}

        Regards,
        EduOS Team
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        logger.info(f"Sent welcome email to {user.email}")
    except CustomUser.DoesNotExist:
        logger.warning(f"Welcome email failed: User ID {user_id} not found")


@shared_task
def send_password_reset_email_task(user_email, reset_link):
    """
    Send password reset email asynchronously.
    """
    try:
        subject = "EduOS Password Reset"
        message = f"""
        You requested a password reset.

        Click the link below to reset your password:
        {reset_link}

        If you didn't request this, please ignore this email.

        EduOS Support Team
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
        logger.info(f"Sent password reset email to {user_email}")
    except Exception as e:
        logger.error(f"Error sending password reset email to {user_email}: {e}")


@shared_task
def notify_suspicious_login_task(user_id, ip_address, user_agent=None):
    """
    Alert user of suspicious login activity.
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
        subject = "EduOS Suspicious Login Detected"
        message = f"""
        Hello {user.first_name},

        A login to your EduOS account was detected from IP address: {ip_address}
        Time: {now().strftime('%Y-%m-%d %H:%M:%S')}
        Device Info: {user_agent or 'Unknown'}

        If this was not you, please reset your password immediately.

        Regards,
        EduOS Security Team
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        logger.warning(f"Suspicious login alert sent to {user.email}")
    except CustomUser.DoesNotExist:
        logger.warning(f"Suspicious login: User ID {user_id} not found")


@shared_task
def log_user_action_task(user_id, action, metadata=None):
    """
    Log user activity (e.g., login, role switch, settings change).
    Could be extended to write to audit log model or external logging system.
    """
    try:
        user = CustomUser.objects.get(pk=user_id)
        logger.info(f"[AUDIT] {user.email} performed '{action}' at {now()} with {metadata or '{}'}")
    except CustomUser.DoesNotExist:
        logger.warning(f"Audit log failed: User ID {user_id} not found")
