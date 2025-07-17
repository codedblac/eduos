from decimal import Decimal
from django.db.models import Sum
from django.utils.crypto import get_random_string
from django.utils import timezone

from students.models import Student
from .models import (
    StudentInvoice, Payment, StudentFinanceSnapshot,
    StudentWallet, WalletTransaction, TransactionLog,
    Budget
)


def calculate_student_balance(student, academic_year, term):
    """
    Returns total invoiced, total paid, and balance for a student.
    """
    total_invoiced = StudentInvoice.objects.filter(
        student=student, academic_year=academic_year, term=term
    ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

    total_paid = StudentInvoice.objects.filter(
        student=student, academic_year=academic_year, term=term
    ).aggregate(total=Sum("amount_paid"))["total"] or Decimal("0.00")

    return {
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "balance": total_invoiced - total_paid
    }


def update_student_snapshot(student, academic_year, term):
    """
    Updates or creates a finance snapshot for a student.
    """
    balances = calculate_student_balance(student, academic_year, term)

    snapshot, _ = StudentFinanceSnapshot.objects.update_or_create(
        student=student,
        academic_year=academic_year,
        term=term,
        defaults=balances
    )
    return snapshot


def format_currency(amount, symbol="KSh"):
    """
    Returns formatted currency string.
    """
    return f"{symbol} {amount:,.2f}"


def generate_receipt_number(institution_id):
    """
    Generate a unique receipt number.
    Format: RCPT-<SchoolID>-YYMMDD-RAND4
    """
    date_code = timezone.now().strftime("%y%m%d")
    random_part = get_random_string(4).upper()
    return f"RCPT-{institution_id}-{date_code}-{random_part}"


def validate_mpesa_code(code):
    """
    Basic MPESA code validator — must be alphanumeric and either 10 or 12 characters.
    """
    return bool(code and len(code) in [10, 12] and code.isalnum())


def credit_wallet(student, amount, reference, status="completed"):
    """
    Credits a student's wallet and logs the transaction.
    """
    wallet, _ = StudentWallet.objects.get_or_create(student=student)

    if wallet.is_frozen:
        raise ValueError("Wallet is currently frozen.")

    wallet.balance += amount
    wallet.save()

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        type="credit",
        reference=reference,
        status=status
    )
    return wallet.balance


def debit_wallet(student, amount, reference, status="completed"):
    """
    Debits a student's wallet and logs the transaction.
    Raises ValueError if balance is insufficient.
    """
    wallet, _ = StudentWallet.objects.get_or_create(student=student)

    if wallet.is_frozen:
        raise ValueError("Wallet is currently frozen.")

    if wallet.balance < amount:
        raise ValueError("Insufficient wallet balance.")

    wallet.balance -= amount
    wallet.save()

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        type="debit",
        reference=reference,
        status=status
    )
    return wallet.balance


def get_budget_summary(budget: Budget):
    """
    Returns income, expense, and variance summary for a given budget.
    """
    income_total = budget.incomes.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    expense_total = budget.expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return {
        "income_total": income_total,
        "expense_total": expense_total,
        "variance": income_total - expense_total
    }


def log_transaction(action, actor, details):
    """
    Utility to create a transaction log.
    """
    TransactionLog.objects.create(
        action=action,
        actor=actor,
        details=details
    )


def summarize_invoice_items(invoice: StudentInvoice):
    """
    Returns a structured breakdown of invoice items and their totals.
    """
    return {
        "items": [
            {
                "fee_item": item.fee_item.name if item.fee_item else "Unnamed",
                "amount": item.amount,
                "discount": item.discount_applied,
                "bursary": item.bursary_applied
            }
            for item in invoice.items.all()
        ],
        "total_amount": invoice.total_amount,
        "balance": invoice.balance
    }
