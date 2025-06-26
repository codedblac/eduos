from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from institutions.models import Institution
from students.models import Student
from classes.models import ClassLevel, Stream
from subjects.models import Subject  
from timetable.models import TimetableEntry  # If lessons are structured by timetable

User = get_user_model()


class AttendanceSource(models.TextChoices):
    MANUAL = 'manual', 'Manual'
    BIOMETRIC = 'biometric', 'Biometric'


class AttendanceStatus(models.TextChoices):
    PRESENT = 'present', 'Present'
    ABSENT = 'absent', 'Absent'


class AbsenceReason(models.Model):
    """
    Institution-specific predefined absence reasons.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.reason


# ------------------------------
# ✅ 1. SCHOOL ATTENDANCE
# ------------------------------

class SchoolAttendanceRecord(models.Model):
    """
    Tracks when a user enters and exits school (students, teachers, staff).
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    entry_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)

    source = models.CharField(max_length=10, choices=AttendanceSource.choices, default=AttendanceSource.MANUAL)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="school_attendance_recorded")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.date} (In: {self.entry_time}, Out: {self.exit_time})"


# ------------------------------
# ✅ 2. CLASS ATTENDANCE
# ------------------------------

class ClassAttendanceRecord(models.Model):
    """
    Tracks lesson/class attendance for students or teachers.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    source = models.CharField(max_length=10, choices=AttendanceSource.choices, default=AttendanceSource.MANUAL)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="class_attendance_recorded")
    recorded_at = models.DateTimeField(auto_now_add=True)

    # For student attendance
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)

    # For teacher attendance (e.g., missed lesson)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons_attended')

    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=10, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    reason = models.ForeignKey(AbsenceReason, on_delete=models.SET_NULL, null=True, blank=True)
    custom_reason = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        who = self.student if self.student else self.teacher
        return f"{who} - {self.date} - {self.subject or 'Lesson'} - {self.status}"
