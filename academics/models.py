import uuid
from django.db import models
from django.utils import timezone
from institutions.models import Institution
from accounts.models import CustomUser


class AcademicYear(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='academic_years')
    name = models.CharField(max_length=50)  # e.g. "2025" or "2025-2026"
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    is_current = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('institution', 'name')
        ordering = ['-start_date']
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


class Term(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=30)  # e.g. "Term 1", "Term 2"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    midterm_date = models.DateField(blank=True, null=True)
    closing_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('academic_year', 'name')
        ordering = ['start_date']
        verbose_name = "Term"
        verbose_name_plural = "Terms"

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"


class HolidayBreak(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='breaks')
    title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = "Holiday / Break"
        verbose_name_plural = "Holiday Breaks"

    def __str__(self):
        return f"{self.title} ({self.term})"


class AcademicEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_school_wide = models.BooleanField(default=True)
    color_code = models.CharField(max_length=7, blank=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = "Academic Event"
        verbose_name_plural = "Academic Events"

    def __str__(self):
        return f"{self.title} ({self.term.name})"


class AcademicAuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    record_id = models.CharField(max_length=100)  # UUID or int
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Academic Audit Log"
        verbose_name_plural = "Academic Audit Logs"

    def __str__(self):
        return f"{self.model_name} {self.action} by {self.actor} at {self.timestamp}"
