from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
from students.models import Student
from classes.models import ClassLevel, Stream

User = settings.AUTH_USER_MODEL


class Wallet(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} - Wallet"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('refund', 'Refund'),
        ('fee_payment', 'Fee Payment'),
        ('topup', 'Top-Up'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField(help_text="E.g., pocket money, trip fee, etc.")
    reference = models.CharField(max_length=255, blank=True, null=True)
    initiated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type.title()} - {self.amount} - {self.wallet.student}"


class MicroFee(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_micro_fees')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    students = models.ManyToManyField(Student, related_name='micro_fees')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.amount}) - {self.teacher}"


class MicroFeePayment(models.Model):
    micro_fee = models.ForeignKey(MicroFee, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    paid_via_wallet = models.BooleanField(default=True)
    payment_reference = models.CharField(max_length=255, blank=True, null=True)
    paid_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('micro_fee', 'student')

    def __str__(self):
        return f"{self.student} paid {self.amount_paid} for {self.micro_fee.title}"


class WalletTopUpRequest(models.Model):
    PAYMENT_METHODS = [
        ('mpesa', 'Mpesa'),
        ('bank', 'Bank Transfer'),
        ('card', 'Card'),
        ('manual', 'Manual'),
        ('other', 'Other'),
    ]

    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_topups')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - Top-up {self.amount} ({self.get_payment_method_display()})"



# e_wallet/models.py

class WalletReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for {self.user} - {'Sent' if self.sent else 'Pending'}"


class WalletPolicy(models.Model):
    institution = models.OneToOneField(Institution, on_delete=models.CASCADE, related_name='wallet_policy')
    max_daily_spend = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    withdrawal_allowed = models.BooleanField(default=False)
    auto_lock_enabled = models.BooleanField(default=False)
    lock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.institution.name} - Wallet Policy"


class WalletAuditLog(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    details = models.TextField()
    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet} - {self.action} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
