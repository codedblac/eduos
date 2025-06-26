from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from institutions.models import Institution
from students.models import Student
from classes.models import ClassLevel, Stream

User = get_user_model()


class DisciplineSeverity(models.TextChoices):
    MINOR = 'minor', 'Minor'
    MODERATE = 'moderate', 'Moderate'
    SEVERE = 'severe', 'Severe'


class DisciplineStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    RESOLVED = 'resolved', 'Resolved'
    ESCALATED = 'escalated', 'Escalated'


class DisciplineCategory(models.Model):
    """
    Institution-defined discipline categories (e.g. Fighting, Cheating, Bullying).
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class DisciplineCase(models.Model):
    """
    A reported discipline issue against a student.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)

    category = models.ForeignKey(DisciplineCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=DisciplineSeverity.choices, default=DisciplineSeverity.MINOR)
    incident_date = models.DateField(default=timezone.now)
    location = models.CharField(max_length=255, blank=True, null=True)

    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_discipline_cases')
    witnesses = models.ManyToManyField(User, blank=True, related_name='witnessed_discipline_cases')

    status = models.CharField(max_length=15, choices=DisciplineStatus.choices, default=DisciplineStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.category} - {self.severity} ({self.status})"


class DisciplinaryAction(models.Model):
    """
    Actions taken for a given case: warning, detention, suspension, etc.
    """
    discipline_case = models.ForeignKey(DisciplineCase, on_delete=models.CASCADE, related_name='actions')
    action_taken = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_discipline_actions')
    date_assigned = models.DateField(default=timezone.now)
    follow_up_required = models.BooleanField(default=False)

    def __str__(self):
        return f"Action for {self.discipline_case} on {self.date_assigned}"
