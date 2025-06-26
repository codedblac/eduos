from django.db import models
from django.conf import settings
from institutions.models import Institution
from staff.models import StaffProfile


class PayrollProfile(models.Model):
    staff_profile = models.OneToOneField(StaffProfile, on_delete=models.CASCADE, related_name='payroll_profile')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    benefits = models.TextField(blank=True, null=True)
    tax_identifier = models.CharField(max_length=100, blank=True, null=True)
    bank_account = models.OneToOneField('BankAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='payroll_profile')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_allowances(self):
        return sum(a.amount for a in self.staff_profile.allowances.all())

    def total_deductions(self):
        return sum(d.amount for d in self.staff_profile.deductions.all())

    def net_salary(self):
        return self.basic_salary + self.total_allowances() - self.total_deductions()

    def __str__(self):
        return f"{self.staff_profile.user.get_full_name()} Payroll"


class Allowance(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    staff_profile = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='allowances')
    is_taxable = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.staff_profile}"


class Deduction(models.Model):
    DEDUCTION_TYPES = [
        ('NSSF', 'NSSF'),
        ('NHIF', 'NHIF'),
        ('PAYE', 'PAYE'),
        ('LOAN', 'Loan'),
        ('DISCIPLINARY', 'Disciplinary'),
        ('ABSENCE', 'Absence'),
        ('OTHER', 'Other'),
    ]
    staff_profile = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='deductions')
    type = models.CharField(max_length=20, choices=DEDUCTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type} - {self.staff_profile}"


class BankAccount(models.Model):
    BANK_CHOICES = [
        ('KCB', 'KCB'),
        ('EQUITY', 'Equity'),
        ('COOP', 'Cooperative'),
        ('ABSA', 'ABSA'),
        ('OTHER', 'Other'),
    ]
    staff_profile = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_name = models.CharField(max_length=100, choices=BANK_CHOICES, default='OTHER')
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, blank=True, null=True)
    is_primary = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_name} - {self.bank_name}"


class SalaryAdvanceRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    staff_profile = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='salary_advances')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    requested_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='advance_reviews')
    reviewed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.staff_profile} - {self.amount} ({self.status})"


class PayrollRun(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='payroll_runs')
    period_start = models.DateField()
    period_end = models.DateField()
    processed_on = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='payroll_processed')
    is_locked = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('institution', 'period_start', 'period_end')

    def __str__(self):
        return f"{self.institution.name} Payroll ({self.period_start} - {self.period_end})"


class Payslip(models.Model):
    staff_profile = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='payslips')
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='payslips')
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    pdf_file = models.FileField(upload_to='payslips/', null=True, blank=True)
    generated_on = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ('staff_profile', 'payroll_run')

    def __str__(self):
        return f"Payslip: {self.staff_profile} - {self.payroll_run}"


class PayrollAuditLog(models.Model):
    staff_profile = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changes = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff_profile.user.username} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
