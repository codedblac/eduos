# e_wallet/tasks.py

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import logging

from .models import (
    WalletTransaction,
    WalletTopUpRequest,
    WalletReminder,
    MicroFee,
    MicroFeePayment
)
from notifications.utils import send_push_notification
from students.models import Student
from accounts.models import CustomUser

logger = logging.getLogger(__name__)


@shared_task
def notify_parent_wallet_top_up(student_id, amount, reference):
    """
    Notifies guardians when a wallet top-up is confirmed.
    """
    try:
        student = Student.objects.select_related('user').prefetch_related('guardians').get(id=student_id)
        guardians = student.guardians.all()
        message = f"KSh {amount} has been added to {student.full_name}'s EduOS Wallet (Ref: {reference})."

        for parent in guardians:
            send_push_notification(
                recipient=parent,
                title="Wallet Top-Up Confirmation",
                message=message
            )
            send_mail(
                subject="EduOS Wallet Top-Up",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[parent.email],
                fail_silently=True
            )
    except Student.DoesNotExist:
        logger.warning(f"Student with ID {student_id} not found for wallet top-up notification.")


@shared_task
def notify_teacher_fee_paid(micro_fee_id):
    """
    Notify teacher that students are paying the posted micro-fee.
    """
    try:
        micro_fee = MicroFee.objects.select_related('teacher').get(id=micro_fee_id)
        teacher = micro_fee.teacher
        message = f"Payments have started for '{micro_fee.title}'. Check fee status in your dashboard."

        send_push_notification(
            recipient=teacher,
            title="Micro-Fee Payment Alert",
            message=message
        )
    except MicroFee.DoesNotExist:
        logger.warning(f"MicroFee with ID {micro_fee_id} not found for teacher notification.")


@shared_task
def auto_archive_old_transactions(days=180):
    """
    Archives wallet transactions older than `days` (default: 180).
    """
    threshold_date = timezone.now() - timezone.timedelta(days=days)
    archived_count = WalletTransaction.objects.filter(
        created_at__lt=threshold_date,
        archived=False
    ).update(archived=True)

    logger.info(f"Archived {archived_count} old wallet transactions.")
    return f"{archived_count} transactions archived."


@shared_task
def send_pending_wallet_reminders():
    """
    Sends unsent reminders related to wallet activity.
    """
    reminders = WalletReminder.objects.filter(sent=False)

    for reminder in reminders:
        send_push_notification(
            recipient=reminder.user,
            title="Wallet Payment Reminder",
            message=reminder.message
        )
        reminder.sent = True
        reminder.sent_at = timezone.now()
        reminder.save()

    logger.info(f"Sent {reminders.count()} wallet reminders.")
    return f"{reminders.count()} reminders sent."


@shared_task
def generate_monthly_wallet_usage_report():
    """
    Placeholder: Generates monthly wallet report for finance dashboards.
    Could include: total top-ups, expenses, balance averages, etc.
    """
    logger.info("Monthly wallet usage report task triggered.")
    # Future logic to aggregate per institution goes here
    pass
