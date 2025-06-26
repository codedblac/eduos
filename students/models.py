from django.db import models
from django.conf import settings
from institutions.models import Institution
from classes.models import Stream, ClassLevel
from teachers.models import Teacher
from django.utils import timezone
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

# class ParentStudentRelationship(models.Model):
#     parent = models.ForeignKey(GuardianProfile, on_delete=models.CASCADE, related_name='children')
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parents')
#     relationship = models.CharField(max_length=50)  # e.g., Father, Mother, Guardian

#     class Meta:
#         unique_together = ('parent', 'student')

#     def __str__(self):
#         return f"{self.parent.user.get_full_name()} → {self.student}"

class MedicalFlag(models.Model):
    """
    Medical alerts such as allergies, chronic conditions, or emergency info.
    Automatically shared with the upcoming medical app.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='medical_flags')
    condition = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    critical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medical: {self.condition} - {self.student}"

class StudentHistory(models.Model):
    """
    Logs changes in enrollment, class levels, or streams for historical tracking.
    Useful for audits, transfers, and ministry compliance.
    """
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
