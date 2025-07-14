from django.db import models
from django.conf import settings
from django.utils import timezone
from subjects.models import Subject
from classes.models import Stream, ClassLevel
from institutions.models import Institution
from students.models import Student


User = settings.AUTH_USER_MODEL

# ----------------------------------------
# Core Exam Models
# ----------------------------------------

class Exam(models.Model):
    TERM_CHOICES = (
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
    )

    name = models.CharField(max_length=100)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name="exams")
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="exams")
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    year = models.PositiveIntegerField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="exams")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_exams")
    created_at = models.DateTimeField(auto_now_add=True)
    is_locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('name', 'class_level', 'stream', 'term', 'year')
        ordering = ['-year', 'term', 'name']

    def __str__(self):
        return f"{self.name} - {self.class_level} {self.stream} ({self.term} {self.year})"


class ExamSchedule(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="schedules")
    publish_date = models.DateTimeField()
    due_date = models.DateTimeField()
    is_visible = models.BooleanField(default=False)


class ExamSubject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    max_score = models.PositiveIntegerField(default=100)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="exam_subjects")

    class Meta:
        unique_together = ('exam', 'subject')

    def __str__(self):
        return f"{self.subject.name} - {self.exam}"


class StudentScore(models.Model):
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE, related_name='scores')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.FloatField()
    grade = models.CharField(max_length=2, blank=True)
    remarks = models.TextField(blank=True)
    position = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('exam_subject', 'student')
        ordering = ['-score']


class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    total_score = models.FloatField()
    average_score = models.FloatField()
    grade = models.CharField(max_length=2, blank=True)
    overall_position = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('exam', 'student')
        ordering = ['-average_score']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.exam.name} Result"


# ----------------------------------------
# Templates, Archives, AI Generation
# ----------------------------------------

class ExamTemplate(models.Model):
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    term = models.CharField(max_length=10, choices=Exam.TERM_CHOICES)
    content = models.TextField()
    marking_scheme = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class ExamArchive(models.Model):
    exam_file = models.FileField(upload_to="exam_archives/")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    term = models.CharField(max_length=10, choices=Exam.TERM_CHOICES)
    year = models.PositiveIntegerField()
    source = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - {self.subject} ({self.year})"


class ExamPrediction(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    term = models.CharField(max_length=10, choices=Exam.TERM_CHOICES)
    year = models.PositiveIntegerField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    predicted_questions = models.JSONField()
    auto_generated_exam = models.TextField(blank=True)
    auto_generated_marking_scheme = models.TextField(blank=True)
    source_summary = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Predictions - {self.subject.name} ({self.term} {self.year})"


# ----------------------------------------
# Grading, Insight & Logs
# ----------------------------------------

class GradeBoundary(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)
    min_score = models.FloatField()
    max_score = models.FloatField()

    class Meta:
        unique_together = ('institution', 'subject', 'grade')
        ordering = ['-min_score']


class ExamInsight(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='insights')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    average_score = models.FloatField()
    highest_score = models.FloatField()
    lowest_score = models.FloatField()
    most_common_grade = models.CharField(max_length=2)
    insight_summary = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)


class GradingEngineLog(models.Model):
    student_score = models.ForeignKey(StudentScore, on_delete=models.CASCADE, related_name="grading_logs")
    source = models.CharField(max_length=100)
    rule_applied = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


# ----------------------------------------
# Automation Tasks & Recurrence
# ----------------------------------------

class ExamTask(models.Model):
    TASK_TYPES = [
        ('generate_exam', 'Generate Exam'),
        ('compile_results', 'Compile Results'),
        ('generate_reports', 'Generate Reports'),
    ]
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="tasks")
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    status = models.CharField(max_length=20, default='pending')
    run_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    run_at = models.DateTimeField(null=True, blank=True)
    error_log = models.TextField(blank=True, null=True)


from institutions.models import Institution  # At the top if not using string reference

class RecurringExamRule(models.Model):
    institution = models.ForeignKey(
        'institutions.Institution',
        on_delete=models.CASCADE,
        related_name='recurring_exam_rules'
    )
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE)
    class_level = models.ForeignKey('classes.ClassLevel', on_delete=models.CASCADE)
    recurrence_type = models.CharField(
        max_length=20,
        choices=[('weekly', 'Weekly'), ('monthly', 'Monthly')]
    )
    last_generated_at = models.DateTimeField(null=True, blank=True)
    exam_template = models.ForeignKey(
        'ExamTemplate',
        on_delete=models.CASCADE,
        related_name='recurring_rules'
    )

    def __str__(self):
        return f"{self.exam_template} | {self.subject} | {self.class_level} | {self.recurrence_type}"
