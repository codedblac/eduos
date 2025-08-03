# fee_management/tasks.py

from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from .models import Invoice, Payment, Penalty, RefundRequest, Receipt, FeeStructure, FeeStructureItem, InvoiceItem
from notifications.utils import notify_user
from students.models import Student
from academics.models import Term
from django.conf import settings

from celery import shared_task
from .models import RefundRequest, Payment
from .utils import process_refund, generate_receipt, calculate_invoice_balance

@shared_task
def task_process_refund(refund_id):
    refund = RefundRequest.objects.get(id=refund_id)
    if refund.status == 'approved':
        process_refund(refund)


@shared_task
def task_generate_receipt(payment_id):
    payment = Payment.objects.get(id=payment_id)
    if payment.status == 'confirmed':
        generate_receipt(payment)
        calculate_invoice_balance(payment.invoice)




@shared_task
def auto_generate_term_invoices():
    """Generate term invoices for all active students, avoiding duplicates."""
    current_term = Term.objects.filter(is_active=True).first()
    if not current_term:
        return

    for student in Student.objects.filter(is_active=True):
        if Invoice.objects.filter(student=student, term=current_term).exists():
            continue

        fee_structure = FeeStructure.objects.filter(
            class_level=student.class_level,
            stream=student.stream,
            term=current_term,
            year=current_term.academic_year,
            institution=student.institution
        ).first()

        if not fee_structure:
            continue  # No applicable fee structure

        invoice = Invoice.objects.create(
            student=student,
            term=current_term,
            year=current_term.academic_year,
            institution=student.institution,
            total_amount=fee_structure.total_amount,
            due_date=timezone.now().date() + timedelta(days=14),
            status='draft'
        )

        for item in FeeStructureItem.objects.filter(structure=fee_structure):
            InvoiceItem.objects.create(
                invoice=invoice,
                fee_item=item.fee_item,
                amount=item.amount
            )


@shared_task
def send_fee_reminders():
    """Notify guardians about upcoming due invoices."""
    today = timezone.now().date()
    due_soon = Invoice.objects.filter(
        is_paid=False,
        due_date__lte=today + timedelta(days=3),
        status__in=['issued', 'overdue']
    )

    for invoice in due_soon:
        user = getattr(invoice.student, 'guardian_user', None)
        if user:
            notify_user(
                user=user,
                title="Upcoming Fee Payment Due",
                message=f"Invoice #{invoice.id} for {invoice.student.full_name()} is due on {invoice.due_date}."
            )


@shared_task
def apply_late_payment_penalties():
    """Automatically apply penalties to overdue invoices (one per term/student)."""
    today = timezone.now().date()
    overdue = Invoice.objects.filter(is_paid=False, due_date__lt=today, status='overdue')

    for invoice in overdue:
        if not Penalty.objects.filter(student=invoice.student, term=invoice.term, waived=False).exists():
            Penalty.objects.create(
                student=invoice.student,
                term=invoice.term,
                amount=100.00,  # Make configurable if needed
                reason="Late Payment Penalty",
                applied_at=timezone.now()
            )


@shared_task
def process_refund_approvals():
    """Auto-approve pending refund requests and notify guardians."""
    pending = RefundRequest.objects.filter(status='pending')

    for request in pending:
        request.status = 'approved'
        request.refunded_on = timezone.now()
        request.save()

        user = getattr(request.student, 'guardian_user', None)
        if user:
            notify_user(
                user=user,
                title="Refund Approved",
                message=f"A refund of KES {request.amount} has been approved for {request.student.full_name()}."
            )


@shared_task
def generate_digital_receipts():
    """Generate PDF receipts for all payments that do not have one."""
    from .utils import create_receipt_pdf

    for payment in Payment.objects.filter(receipt__isnull=True):
        try:
            pdf_url = create_receipt_pdf(payment)
            Receipt.objects.create(
                payment=payment,
                issued_by=payment.received_by,
                pdf_url=pdf_url,
                date_issued=timezone.now()
            )
        except Exception as e:
            # Optional: log or notify error
            print(f"Failed to generate receipt for payment {payment.id}: {e}")
