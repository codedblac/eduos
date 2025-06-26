from django.db.models import Sum
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from finance.models import (
    Refund, ApprovalRequest, FinanceNotification, AnomalyFlag,
    StudentFinanceSnapshot, StudentInvoice, Student,
    Income, Expense
)
from accounts.models import CustomUser
from notifications.utils import notify_user

import logging

logger = logging.getLogger(__name__)


@shared_task
def send_refund_approval_notification(refund_id):
    """
    Notify approver of approved refund.
    """
    try:
        refund = Refund.objects.select_related('student', 'approved_by').get(id=refund_id)
        if refund.approved_by:
            message = f"A refund request of KES {refund.amount} for {refund.student} has been approved."

            FinanceNotification.objects.create(
                recipient=refund.approved_by,
                message=message
            )

            notify_user(
                user=refund.approved_by,
                title="Refund Approved",
                message=message
            )

            logger.info(f"Refund approval notification sent for Refund ID {refund_id}")
    except Refund.DoesNotExist:
        logger.warning(f"Refund ID {refund_id} does not exist.")


@shared_task
def auto_flag_anomalies():
    """
    Flag students whose balance is overdue by more than 30 days.
    """
    overdue_days = 30
    today = timezone.now().date()
    flagged = 0

    for snapshot in StudentFinanceSnapshot.objects.select_related('student').all():
        days_since_update = (today - snapshot.last_updated.date()).days
        if snapshot.balance > 0 and days_since_update > overdue_days:
            anomaly, created = AnomalyFlag.objects.get_or_create(
                student=snapshot.student,
                description="Overdue balance beyond 30 days."
            )
            if created:
                flagged += 1

    logger.info(f"Anomaly flagging completed. {flagged} students flagged.")


@shared_task
def update_finance_snapshots():
    """
    Sync snapshots for all students using their invoices and payments.
    """
    count = 0
    for snapshot in StudentFinanceSnapshot.objects.select_related('student').all():
        invoices = StudentInvoice.objects.filter(
            student=snapshot.student,
            academic_year=snapshot.academic_year,
            term=snapshot.term
        )
        total_invoiced = invoices.aggregate(total=Sum('amount'))['total'] or 0
        total_paid = invoices.aggregate(total=Sum('paid_amount'))['total'] or 0
        balance = total_invoiced - total_paid

        snapshot.total_invoiced = total_invoiced
        snapshot.total_paid = total_paid
        snapshot.balance = balance
        snapshot.save()
        count += 1

    logger.info(f"Finance snapshots updated for {count} student records.")


@shared_task
def generate_daily_financial_summary():
    """
    Sends daily summary to finance admins via in-app and email.
    """
    today = timezone.now().date()
    total_income = Income.objects.filter(received_on=today).aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Expense.objects.filter(spent_on=today).aggregate(total=Sum('amount'))['total'] or 0
    net = total_income - total_expense

    message = (
        f"Daily Financial Summary ({today}):\n"
        f"Income: KES {total_income}\n"
        f"Expense: KES {total_expense}\n"
        f"Net: KES {net}"
    )

    admins = CustomUser.objects.filter(role__in=['admin', 'finance_head'])

    for admin in admins:
        FinanceNotification.objects.create(
            recipient=admin,
            message=message
        )
        notify_user(
            user=admin,
            title="Finance Summary",
            message=message
        )

        if admin.email:
            try:
                send_mail(
                    subject="Daily Finance Summary",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.email],
                    fail_silently=False
                )
            except Exception as e:
                logger.error(f"Failed to send daily summary email to {admin.email}: {str(e)}")

    logger.info(f"Daily finance summary sent to {admins.count()} admins.")


@shared_task
def auto_generate_student_invoices():
    """
    Auto-generates student invoices for current term and year if not already present.
    """
    today = timezone.now().date()
    created = 0

    # Sample logic – you might pull current term/year from your config or AcademicYear model
    from academics.models import Term, AcademicYear
    try:
        current_term = Term.objects.get(is_current=True)
        current_year = AcademicYear.objects.get(is_current=True)
    except Term.DoesNotExist or AcademicYear.DoesNotExist:
        logger.warning("Current academic term or year is not set.")
        return

    for student in Student.objects.all():
        exists = StudentInvoice.objects.filter(
            student=student,
            term=current_term,
            academic_year=current_year
        ).exists()

        if not exists:
            invoice = StudentInvoice.objects.create(
                student=student,
                academic_year=current_year,
                term=current_term,
                amount=0,  # You can set actual fee logic here
                paid_amount=0,
                status='unpaid',
                created_by=None  # Optionally set a system user
            )
            created += 1

    logger.info(f"Auto-generated {created} student invoices.")
