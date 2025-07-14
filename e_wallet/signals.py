# e_wallet/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    WalletTransaction,
    MicroFeePayment,
    WalletReminder,
    WalletTopUpRequest,
    WalletAuditLog,
    Wallet
)
from .tasks import (
    notify_parent_wallet_top_up,
    notify_teacher_fee_paid
)


@receiver(post_save, sender=WalletTransaction)
def handle_wallet_transaction(sender, instance, created, **kwargs):
    """
    When a WalletTransaction is saved:
    - Notify parent if it's a credit/top-up.
    - Log the transaction in WalletAuditLog.
    """
    if not created:
        return

    student = instance.wallet.student
    tx_type = instance.type
    reference = instance.reference or instance.purpose or "N/A"

    # Notify parent if credit/topup
    if tx_type in ['credit', 'topup'] and student:
        notify_parent_wallet_top_up.delay(
            student_id=student.id,
            amount=str(instance.amount),
            reference=reference
        )

    # Audit log entry
    WalletAuditLog.objects.create(
        wallet=instance.wallet,
        action=f"{tx_type.title()} Transaction",
        details=f"{tx_type.title()} of KES {instance.amount} for '{instance.purpose or 'N/A'}' (Ref: {reference})",
        actor=instance.initiated_by
    )


@receiver(post_save, sender=MicroFeePayment)
def handle_micro_fee_payment(sender, instance, created, **kwargs):
    """
    Notify teacher after MicroFeePayment is created.
    """
    if not created:
        return

    micro_fee = instance.micro_fee
    student = instance.student

    if micro_fee and micro_fee.teacher:
        notify_teacher_fee_paid.delay(micro_fee_id=micro_fee.id)

    # Optional audit log for tracking
    WalletAuditLog.objects.create(
        wallet=student.wallet,
        action="Micro-Fee Paid",
        details=f"{student} paid KES {instance.amount_paid} for '{micro_fee.title}'",
        actor=None
    )


@receiver(post_save, sender=WalletTopUpRequest)
def clear_reminders_on_topup_confirmation(sender, instance, **kwargs):
    """
    Resolve related WalletReminders when a top-up is confirmed.
    """
    if instance.confirmed and instance.confirmed_at:
        WalletReminder.objects.filter(
            user=instance.parent,
            related_object_id=instance.id,
            resolved=False
        ).update(
            resolved=True,
            resolved_at=timezone.now()
        )


@receiver(post_save, sender=Wallet)
def log_wallet_creation(sender, instance, created, **kwargs):
    """
    Log when a new wallet is created.
    """
    if created:
        WalletAuditLog.objects.create(
            wallet=instance,
            action="Wallet Created",
            details=f"New wallet created for {instance.student}.",
            actor=None
        )
