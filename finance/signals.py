from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from django.utils import timezone

from finance.models import (
    Income, Expense, Refund, Waiver, StudentFinanceSnapshot,
    TransactionLog, ApprovalRequest, FinanceNotification,
    StudentWallet, WalletTransaction, StudentInvoice
)
from students.models import Student
from accounts.models import CustomUser
from notifications.utils import notify_user

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Income)
def log_income_transaction(sender, instance, created, **kwargs):
    if created and instance.received_by:
        TransactionLog.objects.create(
            action='income',
            actor=instance.received_by,
            details=f"Income recorded: {instance.description} - KES {instance.amount}"
        )
        logger.info(f"Logged income transaction for {instance.amount} by {instance.received_by}")


@receiver(post_save, sender=Expense)
def log_expense_transaction(sender, instance, created, **kwargs):
    if created and instance.spent_by:
        TransactionLog.objects.create(
            action='expense',
            actor=instance.spent_by,
            details=f"Expense recorded: {instance.description} - KES {instance.amount}"
        )
        logger.info(f"Logged expense transaction for {instance.amount} by {instance.spent_by}")


@receiver(post_save, sender=Refund)
def handle_refund_approval(sender, instance, **kwargs):
    if instance.status == 'approved' and instance.approved_by:
        TransactionLog.objects.get_or_create(
            action='refund',
            actor=instance.approved_by,
            details=f"Refund of KES {instance.amount} approved for {instance.student}"
        )

        FinanceNotification.objects.create(
            recipient=instance.approved_by,
            message=f"Refund approved for {instance.student} - KES {instance.amount}"
        )

        notify_user(
            user=instance.approved_by,
            title="Refund Approved",
            message=f"Refund for {instance.student} has been processed and logged."
        )

        logger.info(f"Refund approved and logged for {instance.student}")


@receiver(post_save, sender=Waiver)
def log_waiver_transaction(sender, instance, **kwargs):
    if instance.approved_by and instance.amount > 0:
        TransactionLog.objects.get_or_create(
            action='waiver',
            actor=instance.approved_by,
            details=f"Waiver of KES {instance.amount} approved for {instance.student}"
        )
        logger.info(f"Waiver transaction logged for {instance.student}")


@receiver(post_save, sender=ApprovalRequest)
def send_approval_notification(sender, instance, created, **kwargs):
    if created and instance.status == 'pending' and instance.approved_by:
        FinanceNotification.objects.create(
            recipient=instance.approved_by,
            message=f"Approval required for {instance.request_type.title()} (ID #{instance.reference_id})"
        )

        notify_user(
            user=instance.approved_by,
            title="Approval Request",
            message=f"You have a pending approval for {instance.request_type.title()}."
        )

        logger.info(f"Approval request sent to {instance.approved_by}")


@receiver(post_save, sender=Student)
def create_finance_snapshot_on_student_creation(sender, instance, created, **kwargs):
    if created:
        from academics.models import AcademicYear, Term
        active_year = AcademicYear.objects.filter(is_active=True).first()
        active_term = Term.objects.filter(is_active=True).first()
        if active_year and active_term:
            StudentFinanceSnapshot.objects.get_or_create(
                student=instance,
                academic_year=active_year,
                term=active_term,
                defaults={
                    'total_invoiced': 0,
                    'total_paid': 0,
                    'balance': 0
                }
            )
            logger.info(f"Finance snapshot created for new student {instance}")


@receiver(post_save, sender=StudentWallet)
def notify_low_wallet_balance(sender, instance, **kwargs):
    threshold = 100  # Adjust threshold as needed
    if instance.balance < threshold and hasattr(instance.student, 'user'):
        FinanceNotification.objects.create(
            recipient=instance.student.user,
            message=f"Your wallet balance is low: KES {instance.balance:.2f}"
        )
        logger.info(f"Low balance notification sent to {instance.student}")


@receiver(post_save, sender=WalletTransaction)
def log_wallet_transaction(sender, instance, created, **kwargs):
    if created:
        TransactionLog.objects.create(
            action='income' if instance.type == 'credit' else 'expense',
            actor=None,  # Optional: track bot/system
            details=f"{instance.type.capitalize()} of KES {instance.amount} in wallet. Ref: {instance.reference}"
        )
        logger.info(f"Wallet transaction logged: {instance.type} - {instance.amount}")


@receiver(post_save, sender=StudentInvoice)
def sync_finance_snapshot_on_invoice(sender, instance, **kwargs):
    """
    Sync finance snapshot on invoice create/update.
    """
    snapshot, _ = StudentFinanceSnapshot.objects.get_or_create(
        student=instance.student,
        academic_year=instance.academic_year,
        term=instance.term,
        defaults={
            'total_invoiced': instance.total_amount,
            'total_paid': instance.amount_paid,
            'balance': instance.balance
        }
    )

    # Always recalculate to ensure consistency
    invoices = StudentInvoice.objects.filter(
        student=instance.student,
        academic_year=instance.academic_year,
        term=instance.term
    )

    total_invoiced = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    total_paid = invoices.aggregate(total=Sum('amount_paid'))['total'] or 0

    snapshot.total_invoiced = total_invoiced
    snapshot.total_paid = total_paid
    snapshot.balance = total_invoiced - total_paid
    snapshot.save()

    logger.info(f"Finance snapshot synced for {instance.student} in {instance.term} {instance.academic_year}")
