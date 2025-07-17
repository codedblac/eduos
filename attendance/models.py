from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from institutions.models import Institution
from students.models import Student
from classes.models import ClassLevel, Stream
from subjects.models import Subject
from timetable.models import TimetableEntry

User = get_user_model()


class AttendanceSource(models.TextChoices):
    MANUAL = 'manual', 'Manual'
    BIOMETRIC = 'biometric', 'Biometric'
    QR_CODE = 'qr', 'QR Code'
    API = 'api', 'API'


class AttendanceStatus(models.TextChoices):
    PRESENT = 'present', 'Present'
    ABSENT = 'absent', 'Absent'
    LATE = 'late', 'Late'
    HALF_DAY = 'half_day', 'Half Day'
    EXCUSED = 'excused', 'Excused'


class AbsenceReason(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.reason


class AttendancePolicy(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    allow_half_day = models.BooleanField(default=True)
    grace_period_minutes = models.PositiveIntegerField(default=10)
    auto_mark_absent_if_no_checkin = models.BooleanField(default=True)
    late_threshold_minutes = models.PositiveIntegerField(default=15)

    def __str__(self):
        return f"Attendance Policy - {self.institution}"


class SchoolAttendanceRecord(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    entry_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    is_half_day = models.BooleanField(default=False)
    is_excused = models.BooleanField(default=False)
    source = models.CharField(max_length=15, choices=AttendanceSource.choices, default=AttendanceSource.MANUAL)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="school_attendance_recorded")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.date} (In: {self.entry_time}, Out: {self.exit_time})"


class SchoolAttendanceSession(models.Model):
    attendance = models.ForeignKey(SchoolAttendanceRecord, on_delete=models.CASCADE, related_name='sessions')
    session_type = models.CharField(max_length=50, default='general')
    entry_time = models.TimeField()
    exit_time = models.TimeField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.attendance.user} - {self.session_type}"


class ClassAttendanceRecord(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    source = models.CharField(max_length=15, choices=AttendanceSource.choices, default=AttendanceSource.MANUAL)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="class_attendance_recorded")
    recorded_at = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons_attended')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=15, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    lesson_start_time = models.TimeField(null=True, blank=True)
    lesson_end_time = models.TimeField(null=True, blank=True)
    reason = models.ForeignKey(AbsenceReason, on_delete=models.SET_NULL, null=True, blank=True)
    custom_reason = models.TextField(null=True, blank=True)
    is_makeup_class = models.BooleanField(default=False)
    is_virtual = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        who = self.student or self.teacher
        return f"{who} - {self.date} - {self.subject or 'Lesson'} - {self.status}"


class DailyAttendanceSummary(models.Model):
    date = models.DateField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=AttendanceStatus.choices)
    late_minutes = models.PositiveIntegerField(default=0)
    total_sessions = models.PositiveIntegerField(default=0)
    total_attended = models.PositiveIntegerField(default=0)
    auto_generated = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "date")
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.date} Summary"


class AttendanceDeviceLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    device_id = models.CharField(max_length=100)
    event_type = models.CharField(max_length=10, choices=[('entry', 'Entry'), ('exit', 'Exit')])
    source = models.CharField(max_length=15, choices=AttendanceSource.choices)
    raw_data = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.event_type} - {self.timestamp}"
