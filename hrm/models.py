from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution


class SchoolBranch(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255)
    location = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


class Department(models.Model):
    branch = models.ForeignKey(SchoolBranch, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=255)
    head = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')

    def __str__(self):
        return f"{self.name} - {self.branch.name}"


class StaffHRRecord(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    branch = models.ForeignKey(SchoolBranch, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=100, unique=True)
    date_joined = models.DateField()
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('probation', 'Probation'), ('terminated', 'Terminated'), ('retired', 'Retired')], default='active')
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()


class HRMLog(models.Model):
    ACTION_CATEGORIES = [
        ('staff', 'Staff Profile'),
        ('leave', 'Leave Request'),
        ('performance', 'Performance Review'),
        ('disciplinary', 'Disciplinary Action'),
        ('document', 'Staff Document'),
        ('general', 'General'),
    ]

    staff = models.ForeignKey(StaffHRRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=ACTION_CATEGORIES, default='general')
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'HRM Audit Log'
        verbose_name_plural = 'HRM Audit Logs'

    def __str__(self):
        return f"[{self.category}] {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField()
    requirements = models.TextField()
    is_internal = models.BooleanField(default=False)
    posted_on = models.DateField(default=timezone.now)
    deadline = models.DateField()

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    resume = models.FileField(upload_to='job_applications/')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('interviewed', 'Interviewed'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected')
    ], default='pending')
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant_name} - {self.job.title}"


class Contract(models.Model):
    staff = models.ForeignKey(StaffHRRecord, on_delete=models.CASCADE, related_name='contracts')
    contract_type = models.CharField(max_length=50, choices=[
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
        ('part_time', 'Part Time')
    ])
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    signed_document = models.FileField(upload_to='contracts/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.contract_type}"


class HRDocument(models.Model):
    staff = models.ForeignKey(StaffHRRecord, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=100)
    document = models.FileField(upload_to='hr_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.staff.user.get_full_name()}"


class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    staff = models.ForeignKey(StaffHRRecord, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    requested_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.leave_type.name}"


class AttendanceRecord(models.Model):
    staff = models.ForeignKey(StaffHRRecord, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(blank=True, null=True)
    check_out = models.TimeField(blank=True, null=True)
    method = models.CharField(max_length=50, choices=[
        ('manual', 'Manual'),
        ('biometric', 'Biometric'),
        ('app', 'App')
    ], default='manual')

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.date}"


class PerformanceReview(models.Model):
    staff = models.ForeignKey(StaffHRRecord, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    comments = models.TextField(blank=True, null=True)
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - Review"


class DisciplinaryAction(models.Model):
    staff = models.ForeignKey(StaffHRRecord, on_delete=models.CASCADE, related_name='disciplinary_actions')
    incident_date = models.DateField()
    description = models.TextField()
    outcome = models.TextField()
    resolved = models.BooleanField(default=False)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - Disciplinary"


class HRAuditLog(models.Model):
    staff = models.ForeignKey(StaffHRRecord, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField()

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
