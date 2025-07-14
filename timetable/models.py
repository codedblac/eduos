from django.db import models
from django.utils import timezone
from institutions.models import Institution
from classes.models import Stream, ClassLevel
from subjects.models import Subject
from teachers.models import Teacher
from academics.models import AcademicYear, Term
from accounts.models import CustomUser


class PeriodTemplate(models.Model):
    """
    Defines the time blocks for lessons per day, per class level.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='period_templates')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='period_templates')
    day = models.CharField(max_length=9, choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'),
        ('Saturday', 'Saturday'), ('Sunday', 'Sunday'),
    ])
    period_number = models.PositiveSmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('institution', 'class_level', 'day', 'period_number')
        ordering = ['class_level', 'day', 'period_number']

    def __str__(self):
        return f"{self.class_level.name} | {self.day} P{self.period_number} ({self.start_time}-{self.end_time})"


class Room(models.Model):
    """
    Represents a classroom or specialized room (e.g., lab).
    """
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_lab = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='rooms')

    class Meta:
        unique_together = ('name', 'institution')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


class SubjectAssignment(models.Model):
    """
    Links teachers to subjects and streams, defining teaching responsibilities.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='subject_assignments')
    lessons_per_week = models.PositiveSmallIntegerField()
    is_substitutable = models.BooleanField(default=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='subject_assignments')

    class Meta:
        unique_together = ('teacher', 'subject', 'stream', 'institution')
        ordering = ['stream', 'subject']

    def __str__(self):
        return f"{self.teacher} | {self.subject.name} | {self.stream.name}"


class TimetableVersion(models.Model):
    """
    Groups all timetable entries under a term-based version for an institution.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='timetable_versions')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    is_finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.institution.name} | {self.term.name} | v{self.pk}"


class TimetableEntry(models.Model):
    """
    One scheduled subject period for a stream, within a timetable version.
    """
    version = models.ForeignKey(TimetableVersion, on_delete=models.CASCADE, related_name='entries')
    period_template = models.ForeignKey(PeriodTemplate, on_delete=models.CASCADE, related_name='entries')
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='timetable_entries')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_entries')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='timetable_entries')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_entries')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('version', 'period_template', 'stream')
        ordering = ['period_template__day', 'period_template__start_time']

    def __str__(self):
        return f"{self.stream.name} | {self.subject.name} | {self.period_template.day} P{self.period_template.period_number}"


class TimetableNotificationSetting(models.Model):
    """
    Controls notification behavior per institution for timetable alerts.
    """
    institution = models.OneToOneField(Institution, on_delete=models.CASCADE, related_name='timetable_settings')
    enable_reminders = models.BooleanField(default=True)
    reminder_lead_time_minutes = models.PositiveIntegerField(default=10)
    notify_channels = models.JSONField(default=list)  # e.g., ['popup', 'email']
    daily_overview_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.institution.name} Notification Settings"


class TimetableChangeLog(models.Model):
    """
    Logs changes to timetable entries for auditability.
    """
    entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name='change_logs')
    changed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    change_type = models.CharField(max_length=50, choices=[
        ('created', 'Created'), ('modified', 'Modified'),
        ('rescheduled', 'Rescheduled'), ('cancelled', 'Cancelled')
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.change_type} | {self.entry} | {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class TeacherAvailabilityOverride(models.Model):
    """
    Declares when a teacher is unavailable (e.g., leave, emergency).
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='availability_exceptions')
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    reason = models.TextField(blank=True)
    allowed_to_substitute = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.teacher.user.get_full_name()} unavailable on {self.date}"
