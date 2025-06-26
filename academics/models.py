from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from institutions.models import Institution
from accounts.models import CustomUser


class AcademicYear(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='academic_years')
    name = models.CharField(max_length=50)  # e.g. "2025" or "2025-2026"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('institution', 'name')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


class Term(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=30)  # e.g. "Term 1", "Term 2"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    midterm_date = models.DateField(blank=True, null=True)
    closing_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('academic_year', 'name')
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"


class HolidayBreak(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='breaks')
    title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.term})"


class AcademicEvent(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_school_wide = models.BooleanField(default=True)
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color for calendar display")

    def __str__(self):
        return f"{self.title} ({self.term.name})"


class AcademicAuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    ]

    actor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.model_name} {self.action} by {self.actor} at {self.timestamp}"
