from django.db import models
from django.conf import settings
from institutions.models import Institution
from payroll.models import BankAccount
import uuid

EMPLOYMENT_TYPES = [
    ('full_time', 'Full-Time'),
    ('part_time', 'Part-Time'),
    ('contract', 'Contract'),
    ('volunteer', 'Volunteer'),
]

DESIGNATIONS = [
    ('academic', 'Academic'),
    ('non_academic', 'Non-Academic'),
]

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Core Identity
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='teacher_profile'
    )
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='teachers')

    staff_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='teachers/photos/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    marital_status = models.CharField(max_length=50, blank=True, null=True)
    national_id = models.CharField(max_length=50, blank=True, null=True)

    # Professional Info
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    job_title = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=20, choices=DESIGNATIONS, default='academic')
    joining_date = models.DateField()
    leaving_date = models.DateField(blank=True, null=True)

    subjects_taught = models.ManyToManyField(
        'subjects.Subject',
        blank=True,
        related_name='teachers'
    )
    class_levels_handled = models.ManyToManyField(
        'classes.ClassLevel',
        blank=True,
        related_name='teachers'
    )
    streams_handled = models.ManyToManyField(
        'classes.Stream',
        blank=True,
        related_name='teachers'
    )
    assigned_roles = models.JSONField(blank=True, null=True, help_text="e.g., Head of Department, Exam Coordinator")

    # Qualifications
    qualifications = models.TextField(blank=True, null=True)
    professional_certifications = models.TextField(blank=True, null=True)
    specializations = models.TextField(blank=True, null=True)
    education_history = models.JSONField(blank=True, null=True)
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)

    # Work History
    work_experience = models.JSONField(blank=True, null=True)
    transfer_records = models.JSONField(blank=True, null=True)
    teaching_history = models.JSONField(blank=True, null=True)

    # Digital & AI
    digital_portfolio_url = models.URLField(blank=True, null=True)
    teaching_philosophy = models.TextField(blank=True, null=True)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ai_insights = models.TextField(blank=True, null=True)
    recommended_subjects = models.JSONField(blank=True, null=True)
    student_feedback_summary = models.TextField(blank=True, null=True)
    teacher_ratings = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    disciplinary_flags = models.TextField(blank=True, null=True)

    # Duties
    co_curricular_roles = models.CharField(max_length=255, blank=True, null=True)
    dormitory_duties = models.CharField(max_length=255, blank=True, null=True)
    substitution_availability = models.BooleanField(default=True)
    available_for_virtual_teaching = models.BooleanField(default=False)
    verified_virtual_tutor = models.BooleanField(default=False)
    assigned_virtual_courses = models.JSONField(blank=True, null=True)

    # Contact & Emergency
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    alternative_contact = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True, null=True)
    residence_address = models.TextField(blank=True, null=True)
    postal_address = models.TextField(blank=True, null=True)
    next_of_kin = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_relationship = models.CharField(max_length=50, blank=True, null=True)

    # Payroll & HR
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, blank=True, null=True)
    salary_scale = models.CharField(max_length=50, blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, null=True)
    payroll_profile = models.CharField(max_length=100, blank=True, null=True)
    contract_renewal_due = models.DateField(blank=True, null=True)
    promotion_due = models.DateField(blank=True, null=True)
    leave_balance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    # Attendance & Leave
    daily_checkin_logs = models.JSONField(blank=True, null=True)
    teacher_absenteeism_records = models.JSONField(blank=True, null=True)
    leave_history = models.JSONField(blank=True, null=True)
    approved_leave_days = models.PositiveIntegerField(default=0)

    # Misc
    is_active = models.BooleanField(default=True)
    timetable_pdf = models.FileField(upload_to='teachers/timetables/', blank=True, null=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        unique_together = ('institution', 'staff_id')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.staff_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name}".strip()
