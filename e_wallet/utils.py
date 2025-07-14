# e_wallet/utils.py

from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Wallet, WalletTransaction, WalletAuditLog
from students.models import Student
from finance.models import FinanceNotification


def get_or_create_wallet(student: Student) -> Wallet:
    """
    Ensure a wallet exists for the given student.
    """
    wallet, created = Wallet.objects.get_or_create(
        student=student,
        defaults={'institution': student.institution}
    )
    return wallet


@transaction.atomic
def credit_wallet(student: Student, amount: Decimal, purpose: str = "Top-Up", reference: str = "", actor=None, notify=True) -> WalletTransaction:
    """
    Credit (add funds to) a student's wallet.
    """
    if amount <= 0:
        raise ValidationError("Credit amount must be greater than zero.")

    wallet = get_or_create_wallet(student)
    wallet.balance += amount
    wallet.save()

    transaction_obj = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        type='credit',
        purpose=purpose,
        reference=reference,
        initiated_by=actor
    )

    WalletAuditLog.objects.create(
        wallet=wallet,
        action='credit',
        details=f"KES {amount} credited. Reason: {purpose}",
        actor=actor
    )

    if notify:
        _notify_wallet_activity(student, f"KES {amount} credited to wallet. Purpose: {purpose}. Ref: {reference or 'N/A'}")

    return transaction_obj


@transaction.atomic
def debit_wallet(student: Student, amount: Decimal, purpose: str = "Charge", reference: str = "", actor=None, notify=True) -> WalletTransaction:
    """
    Debit (deduct funds from) a student's wallet.
    """
    wallet = get_or_create_wallet(student)

    if amount <= 0:
        raise ValidationError("Debit amount must be greater than zero.")

    if wallet.balance < amount:
        raise ValidationError("Insufficient balance in the wallet.")

    wallet.balance -= amount
    wallet.save()

    transaction_obj = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        type='debit',
        purpose=purpose,
        reference=reference,
        initiated_by=actor
    )

    WalletAuditLog.objects.create(
        wallet=wallet,
        action='debit',
        details=f"KES {amount} debited. Reason: {purpose}",
        actor=actor
    )

    if notify:
        _notify_wallet_activity(student, f"KES {amount} debited from wallet. Reason: {purpose}. Ref: {reference or 'N/A'}")

    return transaction_obj


def check_wallet_balance(student: Student) -> Decimal:
    """
    Return the current wallet balance.
    """
    return get_or_create_wallet(student).balance


def _notify_wallet_activity(student: Student, message: str):
    """
    Notify student (or their guardian) about wallet activity.
    """
    FinanceNotification.objects.create(
        recipient=student.user,
        message=message
    )
