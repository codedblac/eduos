from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
from academics.models import AcademicYear, Term
from students.models import Student
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = settings.AUTH_USER_MODEL


class Currency(models.Model):
    code = models.CharField(max_length=5, default='KES')
    symbol = models.CharField(max_length=5, default='KSh')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} ({self.symbol})"


class CurrencyRateHistory(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rate_history')
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    recorded_at = models.DateTimeField(auto_now_add=True)


class FundSource(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=[
        ("government", "Government"),
        ("donor", "Donor"),
        ("parent", "Parent"),
        ("partner", "Partner"),
    ])
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Budget(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    total_income_estimate = models.DecimalField(max_digits=12, decimal_places=2)
    total_expense_estimate = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_budgets')
    approved_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.institution} - {self.term} {self.academic_year} Budget"


class Income(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='incomes')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    received_on = models.DateField(default=timezone.now)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    source = models.ForeignKey(FundSource, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Income: {self.description} - {self.amount}"


class Expense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_on = models.DateField(default=timezone.now)
    spent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Expense: {self.description} - {self.amount}"


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey('StudentInvoice', on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)


class Refund(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    ref_number = models.CharField(max_length=100, unique=True)
    document = models.FileField(upload_to='refund_documents/', blank=True, null=True)
    requested_on = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    approved_on = models.DateTimeField(null=True, blank=True)
    processed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund for {self.student} - {self.amount}"


class Waiver(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_on = models.DateTimeField(null=True, blank=True)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self):
        return f"Waiver for {self.student} - {self.amount}"


class StudentWallet(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_frozen = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student}: Wallet Balance {self.balance}"


class WalletTransaction(models.Model):
    wallet = models.ForeignKey(StudentWallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    reference = models.CharField(max_length=255)
    source = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('reversed', 'Reversed')], default='completed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type.capitalize()} - {self.amount}"


class StudentFinanceSnapshot(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="finance_snapshots")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    total_invoiced = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Snapshot for {self.student} ({self.term} {self.academic_year})"


class StudentInvoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100, unique=True)
    issued_on = models.DateField(default=timezone.now)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue')
    ], default='unpaid')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_status(self):
        if self.balance <= 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        elif timezone.now().date() > self.due_date:
            self.status = 'overdue'
        else:
            self.status = 'unpaid'
        self.save()

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.student}"


class TransactionLog(models.Model):
    ACTION_CHOICES = [
        ('income', 'Income Entry'),
        ('expense', 'Expense Entry'),
        ('refund', 'Refund Processed'),
        ('waiver', 'Waiver Approved')
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.get_action_display()} by {self.actor} on {self.timestamp}"


class ApprovalRequest(models.Model):
    request_type = models.CharField(max_length=50)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='finance_approver')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])
    requested_on = models.DateTimeField(auto_now_add=True)
    approved_on = models.DateTimeField(null=True, blank=True)


class FinanceNotification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, default='info')
    message = models.TextField()
    action_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"FinanceNotification to {self.recipient}"


class AnomalyFlag(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    description = models.TextField()
    flagged_on = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Anomaly for {self.student}"


class ScholarshipCandidate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    score = models.FloatField()
    need_score = models.FloatField()
    recommended_by_ai = models.BooleanField(default=False)

    def __str__(self):
        return f"Candidate: {self.student}"


class RecurringTransaction(models.Model):
    TRANSACTION_TYPE = [('income', 'Income'), ('expense', 'Expense')]

    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('termly', 'Termly')])
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_run = models.DateField()
    active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.type.title()} - {self.description}"


class JournalEntry(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.TextField()
    debit_account = models.CharField(max_length=100)
    credit_account = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_reconciled = models.BooleanField(default=False)

    def __str__(self):
        return f"Journal: {self.description} - {self.amount}"


class AuditTrail(models.Model):
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    action = models.CharField(max_length=50)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Audit: {self.model_name} - {self.action}"


class ChartOfAccount(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[('asset', 'Asset'), ('liability', 'Liability'), ('equity', 'Equity'), ('income', 'Income'), ('expense', 'Expense')])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
