from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from institutions.models import Institution
from students.models import Student
from classes.models import ClassLevel, Stream
from subjects.models import Subject
from exams.models import Exam


class ReportType(models.TextChoices):
    ACADEMICS = 'academics', 'Academics'
    FINANCE = 'finance', 'Finance'
    ATTENDANCE = 'attendance', 'Attendance'
    DISCIPLINE = 'discipline', 'Discipline'
    MEDICAL = 'medical', 'Medical'
    OVERVIEW = 'overview', 'Institution Overview'
    CUSTOM = 'custom', 'Custom Report'


class ReportAccessLevel(models.TextChoices):
    ADMIN = 'admin', 'Admin Only'
    TEACHER = 'teacher', 'Teachers'
    GUARDIAN = 'guardian', 'Guardians'
    STUDENT = 'student', 'Students'


class ReportStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    FINALIZED = 'finalized', 'Finalized'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class GeneratedReport(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    access_level = models.CharField(max_length=20, choices=ReportAccessLevel.choices, default=ReportAccessLevel.ADMIN)
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.DRAFT)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_reports')
    date_generated = models.DateTimeField(default=timezone.now)
    is_auto_generated = models.BooleanField(default=False)

    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    term = models.CharField(max_length=20, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)

    file = models.FileField(upload_to='reports/', blank=True, null=True)
    json_data = models.JSONField(blank=True, null=True)
    ai_summary = models.TextField(blank=True, null=True)
    smart_flags = models.JSONField(blank=True, null=True)

    version = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_generated']
        indexes = [
            models.Index(fields = ['institution', 'report_type', 'term', 'year']),
            models.Index(fields = ['class_level', 'stream', 'year', 'term']),
        ]
        constraints = [
            models.UniqueConstraint(fields = ['institution', 'report_type', 'term', 'year', 'class_level', 'stream'], name='unique_report_version', violation_error_message="Report already exists for class and term."),
        ]

    def __str__(self):
        return f"{self.title} ({self.report_type}) [{self.term} {self.year}]"

    def is_published(self):
        return self.status == ReportStatus.PUBLISHED


class ReportStudentPerformance(models.Model):
    report = models.ForeignKey(GeneratedReport, on_delete=models.CASCADE, related_name='student_performances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    total_marks = models.FloatField()
    mean_score = models.FloatField()
    grade = models.CharField(max_length=10)
    rank = models.PositiveIntegerField()
    position_out_of = models.PositiveIntegerField()

    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True)

    comment = models.TextField(blank=True, null=True)
    remedial_suggestion = models.TextField(blank=True, null=True)
    flagged = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.grade} (Rank {self.rank})"


class ReportSubjectBreakdown(models.Model):
    report = models.ForeignKey(GeneratedReport, on_delete=models.CASCADE, related_name='subject_breakdowns')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='subject_breakdown_teacher')

    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True, blank=True)

    average_score = models.FloatField()
    top_score = models.FloatField()
    lowest_score = models.FloatField()
    pass_rate = models.FloatField()
    failure_rate = models.FloatField()
    most_common_grade = models.CharField(max_length=10, blank=True, null=True)

    comment = models.TextField(blank=True, null=True)
    flagged = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} | {self.class_level} | {self.exam}"


class ReportAuditTrail(models.Model):
    report = models.ForeignKey(GeneratedReport, on_delete=models.CASCADE, related_name="audit_trails")
    action = models.CharField(max_length=255)
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.report.title} - {self.action} by {self.performed_by}"


class ReportPrintRequest(models.Model):
    report = models.ForeignKey(GeneratedReport, on_delete=models.CASCADE, related_name="print_requests")
    requested_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    requested_at = models.DateTimeField(default=timezone.now)
    copies = models.PositiveIntegerField(default=1)
    print_center_notes = models.TextField(blank=True, null=True)
    printed_file = models.FileField(upload_to='reports/print/', blank=True, null=True)

    is_printed = models.BooleanField(default=False)
    printed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"PrintRequest: {self.report.title} by {self.requested_by}"
