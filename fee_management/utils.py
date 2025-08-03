# fee_management/utils.py

import uuid
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone

from .models import (
    Invoice, Payment, BursaryAllocation, Penalty,
    FeeStructure, Receipt, RefundRequest, FeeItem, InvoiceItem
)
from students.models import Student


def generate_invoice_number():
    """
    Generate a unique invoice identifier.
    """
    return f"INV-{uuid.uuid4().hex[:8].upper()}"


def calculate_invoice_balance(invoice: Invoice) -> Decimal:
    """
    Recalculate and update the current balance due on an invoice.
    """
    total_paid = Payment.objects.filter(
        invoice=invoice, status='confirmed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    new_balance = Decimal(invoice.total_amount) - total_paid
    invoice.balance_due = round(new_balance, 2)
    invoice.is_paid = new_balance <= 0
    invoice.status = 'paid' if invoice.is_paid else invoice.status
    invoice.save(update_fields=['balance_due', 'is_paid', 'status'])

    return invoice.balance_due


def get_student_outstanding_balance(student: Student, term, year) -> Decimal:
    """
    Calculate the student's total unpaid amount across all invoices in a term and year.
    """
    invoices = Invoice.objects.filter(student=student, term=term, year=year, is_paid=False)
    return invoices.aggregate(total=Sum('balance_due'))['total'] or Decimal('0.00')


def apply_penalty(student: Student, term, reason: str, amount: float) -> Penalty:
    """
    Apply a penalty to a student's account.
    """
    penalty = Penalty.objects.create(
        student=student,
        term=term,
        amount=Decimal(amount),
        reason=reason
    )
    return penalty


def get_applicable_fee_structure(student: Student, term, year) -> FeeStructure:
    """
    Get the applicable fee structure for a student.
    """
    return FeeStructure.objects.filter(
        class_level=student.class_level,
        stream=student.stream,
        term=term,
        year=year,
        institution=student.institution
    ).first()


def sum_bursaries(student: Student, term, year) -> Decimal:
    """
    Sum all bursary allocations for a student in a given term and year.
    """
    return BursaryAllocation.objects.filter(
        student=student, term=term, year=year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')


def validate_receipt_number(receipt_number: str) -> bool:
    """
    Check if a given receipt number is already used.
    """
    return not Receipt.objects.filter(receipt_number=receipt_number).exists()


def generate_receipt(payment: Payment) -> Receipt:
    """
    Generate a receipt for a confirmed payment.
    """
    if not payment.status == 'confirmed':
        raise ValueError("Only confirmed payments can have receipts.")

    receipt, created = Receipt.objects.get_or_create(
        payment=payment,
        defaults={
            'issued_by': payment.received_by,
            'filename': f"receipt_{payment.id}.pdf"
        }
    )
    return receipt


def calculate_total_invoice_amount(items: list[InvoiceItem]) -> Decimal:
    """
    Calculate total invoice amount including any applied discounts/bursaries.
    """
    total = Decimal('0.00')
    for item in items:
        subtotal = Decimal(item.amount) - Decimal(item.discount_applied or 0) - Decimal(item.bursary_applied or 0)
        total += max(subtotal, Decimal('0.00'))
    return total


def process_refund(refund: RefundRequest):
    """
    Finalize a refund request by marking it refunded.
    """
    if refund.status != 'approved':
        raise ValueError("Only approved refund requests can be processed.")

    refund.refunded_on = timezone.now()
    refund.save(update_fields=['refunded_on'])
