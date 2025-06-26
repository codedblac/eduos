from django.db import models
from institutions.models import Institution
from classes.models import Stream
from subjects.models import Subject
from teachers.models import Teacher


class Period(models.Model):
    """Defines a specific lesson slot within an institution."""
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
    ]
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='periods')

    class Meta:
        unique_together = ('day', 'start_time', 'institution')
        ordering = ['day', 'start_time']
        verbose_name = "Period"
        verbose_name_plural = "Periods"

    def __str__(self):
        return f"{self.get_day_display()} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class Room(models.Model):
    """Physical or virtual room for lessons."""
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_lab = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='rooms')

    class Meta:
        unique_together = ('name', 'institution')  # Prevent duplicate room names per institution
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


class SubjectAssignment(models.Model):
    """
    Links a teacher to a subject and a stream with weekly lesson frequency.
    Ensures assignments are institution-scoped.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='subject_assignments')
    lessons_per_week = models.PositiveSmallIntegerField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='subject_assignments')

    class Meta:
        unique_together = ('teacher', 'subject', 'stream', 'institution')
        verbose_name = "Subject Assignment"
        verbose_name_plural = "Subject Assignments"

    def __str__(self):
        return f"{self.teacher.user.get_full_name()} - {self.subject.name} - {self.stream.name} ({self.institution.name})"


class TimetableEntry(models.Model):
    """
    Final AI-generated or manually created timetable entry.
    Uniqueness enforced on period + stream + institution for conflict-free scheduling.
    """
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='entries')
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name='timetable_entries')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_entries')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='timetable_entries')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_entries')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='timetable_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Track updates for audit & AI feedback

    class Meta:
        unique_together = ('period', 'stream', 'institution')
        ordering = ['period__day', 'period__start_time']
        verbose_name = "Timetable Entry"
        verbose_name_plural = "Timetable Entries"

    def __str__(self):
        return (
            f"{self.stream.name} - {self.subject.name} - "
            f"{self.teacher.user.get_full_name()} @ {self.period} ({self.institution.name})"
        )
