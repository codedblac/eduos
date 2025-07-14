from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
from students.models import Student

GUARDIAN_NOTIFICATION_TYPES = [
    ("exam_update", "Exam Update"),
    ("fee_balance", "Fee Balance"),
    ("medical_alert", "Medical Alert"),
    ("timetable_update", "Timetable Update"),
    ("announcement", "General Announcement"),
    ("discipline", "Discipline Alert"),
    ("chat", "New Chat Message"),
    ("wallet", "Wallet Activity"),
]

RELATIONSHIP_CHOICES = [
    ("father", "Father"),
    ("mother", "Mother"),
    ("guardian", "Guardian"),
    ("sponsor", "Sponsor"),
    ("uncle", "Uncle"),
    ("aunt", "Aunt"),
    ("grandparent", "Grandparent"),
    ("other", "Other"),
]

class Guardian(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guardian_profile')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="guardians")

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'institution')
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class GuardianStudentLink(models.Model):
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name="student_links")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="guardian_links")
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('guardian', 'student')
        ordering = ['-is_primary', 'relationship']

    def __str__(self):
        return f"{self.guardian} → {self.student} ({self.relationship})"


class GuardianNotification(models.Model):
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name="notifications")
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="guardian_notifications")

    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=GUARDIAN_NOTIFICATION_TYPES)
    related_object_type = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., 'medical.MedicalVisit'")
    related_object_id = models.CharField(max_length=100, blank=True, null=True, help_text="Primary key of the related object")

    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.title} → {self.guardian.user.username}"
