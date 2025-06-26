from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
from students.models import Student
from academics.models import AcademicYear, Term
from classes.models import ClassLevel, Stream

User = settings.AUTH_USER_MODEL


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FeeItem(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_mandatory = models.BooleanField(default=True)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    term = models.ForeignKey(Term, on_delete=models.SET_NULL, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FeeStructure(TimeStampedModel):
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    items = models.ManyToManyField(FeeItem, through='FeeStructureItem')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.class_level} - {self.term} - {self.year}"


class FeeStructureItem(models.Model):
    structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    fee_item = models.ForeignKey(FeeItem, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class Invoice(TimeStampedModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    due_date = models.DateField()
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invoices_issued')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_paid = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'term', 'year')

    def __str__(self):
        return f"Invoice #{self.id} - {self.student}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    fee_item = models.ForeignKey(FeeItem, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bursary_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


class Payment(TimeStampedModel):
    MODE_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
        ('bursary', 'Bursary'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reference_code = models.CharField(max_length=100, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_gateway_response = models.JSONField(blank=True, null=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    paid_at = models.DateTimeField(default=timezone.now)
    paid_by = models.CharField(max_length=255)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments_received')
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student} - {self.amount} via {self.mode}"


class Receipt(TimeStampedModel):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_issued = models.DateTimeField(auto_now_add=True)
    pdf_url = models.URLField(blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True)


class Penalty(TimeStampedModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    waived = models.BooleanField(default=False)


class BursaryAllocation(TimeStampedModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=255)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    invoice_item = models.ForeignKey(InvoiceItem, on_delete=models.SET_NULL, null=True, blank=True)


class RefundRequest(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='refunds_requested')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='refunds_approved')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    refunded_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund for {self.student} - {self.status}"
