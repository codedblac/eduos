from django.db.models import Sum
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from decimal import Decimal
import logging

from finance.models import (
    Refund, FinanceNotification, AnomalyFlag,
    StudentFinanceSnapshot, StudentInvoice, Student,
    Income, Expense, Budget
)
from accounts.models import CustomUser
from academics.models import AcademicYear, Term
from notifications.utils import notify_user
from finance.utils import generate_receipt_number

logger = logging.getLogger(__name__)


@shared_task
def send_refund_approval_notification(refund_id):
    """Notify approver of approved refund."""
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
    """Flag students whose balance is overdue by more than 30 days."""
    overdue_days = 30
    today = timezone.now().date()
    flagged = 0

    for snapshot in StudentFinanceSnapshot.objects.select_related('student').all():
        if snapshot.balance > 0:
            days_since_update = (today - snapshot.last_updated.date()).days
            if days_since_update > overdue_days:
                _, created = AnomalyFlag.objects.get_or_create(
                    student=snapshot.student,
                    description="Overdue balance beyond 30 days."
                )
                if created:
                    flagged += 1

    logger.info(f"Anomaly flagging completed. {flagged} students flagged.")


@shared_task
def update_finance_snapshots():
    """Sync finance snapshots for all students using invoice data."""
    count = 0
    for snapshot in StudentFinanceSnapshot.objects.select_related('student').all():
        invoices = StudentInvoice.objects.filter(
            student=snapshot.student,
            academic_year=snapshot.academic_year,
            term=snapshot.term
        )
        total_invoiced = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal("0.00")
        total_paid = invoices.aggregate(total=Sum('amount_paid'))['total'] or Decimal("0.00")
        balance = total_invoiced - total_paid

        snapshot.total_invoiced = total_invoiced
        snapshot.total_paid = total_paid
        snapshot.balance = balance
        snapshot.save()
        count += 1

    logger.info(f"Finance snapshots updated for {count} student records.")


@shared_task
def generate_daily_financial_summary():
    """Send daily income/expense/net summary to finance admins."""
    today = timezone.now().date()
    total_income = Income.objects.filter(received_on=today).aggregate(total=Sum('amount'))['total'] or Decimal("0.00")
    total_expense = Expense.objects.filter(spent_on=today).aggregate(total=Sum('amount'))['total'] or Decimal("0.00")
    net = total_income - total_expense

    message = (
        f"Daily Financial Summary ({today}):\n"
        f"Income: KES {total_income:,.2f}\n"
        f"Expense: KES {total_expense:,.2f}\n"
        f"Net: KES {net:,.2f}"
    )

    admins = CustomUser.objects.filter(role__in=['admin', 'finance_head'])

    for admin in admins:
        FinanceNotification.objects.create(
            recipient=admin,
            message=message
        )
        notify_user(user=admin, title="Finance Summary", message=message)

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
                logger.error(f"Email send failed to {admin.email}: {str(e)}")

    logger.info(f"Finance summary sent to {admins.count()} admins.")


@shared_task
def auto_generate_student_invoices():
    """Auto-generate invoices for current term and year if not already existing."""
    today = timezone.now().date()
    created = 0

    try:
        current_term = Term.objects.get(is_current=True)
        current_year = AcademicYear.objects.get(is_current=True)
    except (Term.DoesNotExist, AcademicYear.DoesNotExist):
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
                invoice_number=generate_receipt_number(student.institution_id),
                issued_on=today,
                due_date=today + timezone.timedelta(days=30),
                total_amount=Decimal("0.00"),
                amount_paid=Decimal("0.00"),
                balance=Decimal("0.00"),
                status='unpaid',
                created_by=None  # Optional: replace with system/bot user
            )
            invoice.update_status()
            created += 1

    logger.info(f"Auto-generated {created} student invoices.")
