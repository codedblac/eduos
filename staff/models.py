from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from institutions.models import Institution
from departments.models import Department


class StaffCategory(models.TextChoices):
    TEACHING = 'teaching', 'Teaching Staff'
    NON_TEACHING = 'non_teaching', 'Non-Teaching Staff'
    SUPPORT = 'support', 'Support Staff'


class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='staff')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')
    staff_category = models.CharField(max_length=20, choices=StaffCategory.choices)
    job_title = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=15)
    date_joined = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.job_title})"

class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_handle = models.CharField(max_length=100, blank=True, null=True)
    facebook_profile = models.URLField(blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"

class EmploymentHistory(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='employment_history')
    position = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    employment_type = models.CharField(max_length=20)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.position} ({self.start_date})"


class StaffQualification(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='qualifications')
    qualification = models.CharField(max_length=200)
    institution_name = models.CharField(max_length=200)
    year_awarded = models.PositiveIntegerField()
    document = models.FileField(upload_to='staff_qualifications/', blank=True, null=True)

    class Meta:
        ordering = ['-year_awarded']

    def __str__(self):
        return f"{self.qualification} - {self.institution_name}"


class StaffLeave(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_staff_leaves')
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.staff.user.get_full_name()} Leave ({self.start_date} - {self.end_date})"


class StaffDisciplinaryAction(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='disciplinary_actions')
    action_taken = models.TextField()
    date_reported = models.DateField()
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_disciplinary_actions')
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_reported']

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - Action on {self.date_reported}"


class StaffAttendance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('on_leave', 'On Leave'),
        ('late', 'Late'),
    ])
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('staff', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.date} ({self.status})"
