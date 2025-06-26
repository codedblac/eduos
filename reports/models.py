from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from institutions.models import Institution
from students.models import Student
from classes.models import ClassLevel, Stream
from subjects.models import Subject
from exams.models import Exam



# -------------------------------
# Report Metadata
# -------------------------------

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


class GeneratedReport(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    access_level = models.CharField(max_length=20, choices=ReportAccessLevel.choices, default=ReportAccessLevel.ADMIN)
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    date_generated = models.DateTimeField(default=timezone.now)
    is_auto_generated = models.BooleanField(default=False)

    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    term = models.CharField(max_length=50, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)

    file = models.FileField(upload_to='reports/', blank=True, null=True)
    json_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.report_type}) for {self.institution}"


# -------------------------------
# Academic Breakdown
# -------------------------------

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

    def __str__(self):
        return f"{self.student} - {self.grade} (Rank {self.rank})"


class ReportSubjectBreakdown(models.Model):
    report = models.ForeignKey(GeneratedReport, on_delete=models.CASCADE, related_name='subject_breakdowns')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_subjects')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)

    exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True, blank=True)
    average_score = models.FloatField()
    top_score = models.FloatField()
    lowest_score = models.FloatField()
    pass_rate = models.FloatField(help_text="Percentage of students who passed (0-100)")
    failure_rate = models.FloatField()
    most_common_grade = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.subject} - {self.stream} - {self.exam}"
