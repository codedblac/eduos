from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
from classes.models import Stream, ClassLevel
from teachers.models import Teacher
import uuid

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]

ENROLLMENT_STATUS = [
    ('active', 'Active'),
    ('suspended', 'Suspended'),
    ('graduated', 'Graduated'),
    ('transferred', 'Transferred'),
    ('inactive', 'Inactive'),
    ('expelled', 'Expelled'),
]


def student_photo_path(instance, filename):
    return f"students/{instance.institution.id}/{instance.admission_number}/photo/{filename}"


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='students')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    admission_number = models.CharField(max_length=50, unique=True)

    national_id = models.CharField(max_length=50, blank=True, null=True)
    birth_certificate_number = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    photo = models.ImageField(upload_to=student_photo_path, blank=True, null=True)

    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    enrollment_status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='active')
    date_joined = models.DateField(default=timezone.now)
    date_left = models.DateField(null=True, blank=True)

    assigned_class_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students'
    )

    religion = models.CharField(max_length=50, blank=True, null=True)
    disability = models.CharField(max_length=100, blank=True, null=True)
    health_notes = models.TextField(blank=True, null=True)

    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_boarding = models.BooleanField(default=False)

    parent_access_code = models.CharField(max_length=50, blank=True, null=True, help_text="Unique code for guardian mobile login")

    # === AI-enhanced fields ===
    ai_insights = models.TextField(blank=True, null=True, help_text="Full AI-generated performance summary")
    performance_comments = models.TextField(blank=True, null=True, help_text="Readable comments from AI")
    recommended_books = models.JSONField(blank=True, null=True, help_text="AI-suggested books")
    recommended_teachers = models.JSONField(blank=True, null=True, help_text="AI-suggested teachers or mentors")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('institution', 'admission_number')
        ordering = ['class_level', 'stream', 'last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"


class GuardianRelationship(models.Model):
    guardian = models.ForeignKey('guardians.Guardian', on_delete=models.CASCADE, related_name='linked_students')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='linked_guardians')
    relationship = models.CharField(max_length=50)  # e.g., Father, Aunt, Sponsor
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('guardian', 'student')


class StudentDocument(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=100)
    document = models.FileField(upload_to='students/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.student}"


class StudentExitRecord(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='exit_record')
    reason = models.CharField(max_length=100, choices=ENROLLMENT_STATUS)
    exit_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.reason} on {self.exit_date}"


class AcademicSnapshot(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_snapshots')
    term = models.CharField(max_length=50)
    year = models.IntegerField()
    average_score = models.DecimalField(max_digits=5, decimal_places=2)
    behavior_rating = models.PositiveIntegerField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.term} {self.year}"


class MedicalFlag(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='medical_flags')
    condition = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    critical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medical: {self.condition} - {self.student}"


class StudentHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    change_type = models.CharField(max_length=50)  # e.g., "Transferred", "Promoted", "Suspended"
    old_class = models.ForeignKey(ClassLevel, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    new_class = models.ForeignKey(ClassLevel, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    old_stream = models.ForeignKey(Stream, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    new_stream = models.ForeignKey(Stream, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    date_changed = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_changed']

    def __str__(self):
        return f"{self.student} - {self.change_type} on {self.date_changed.strftime('%Y-%m-%d')}"
