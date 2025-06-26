from django.db import models

# Create your models here.
# exams/models.py

from django.db import models
from django.conf import settings
from subjects.models import Subject
from classes.models import Stream, ClassLevel
from institutions.models import Institution
from students.models import Student
student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
teacher = models.ForeignKey("teachers.Teacher", on_delete=models.SET_NULL, null=True, blank=True)


# -----------------------------------------------------
# Core Exam Structure
# -----------------------------------------------------

class Exam(models.Model):
    TERM_CHOICES = (
        ('term1', 'Term 1'),
        ('term2', 'Term 2'),
        ('term3', 'Term 3'),
    )

    name = models.CharField(max_length=100)  # e.g., Mid Term 1
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    year = models.PositiveIntegerField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'class_level', 'stream', 'term', 'year')
        ordering = ['-year', 'term', 'name']

    def __str__(self):
        return f"{self.name} - {self.class_level.name} {self.stream.name} ({self.term} {self.year})"


class ExamSubject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    max_score = models.PositiveIntegerField(default=100)

    class Meta:
        unique_together = ('exam', 'subject')

    def __str__(self):
        return f"{self.subject.name} - {self.exam}"



class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
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

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.exam_subject.subject.name}: {self.score}"


# -----------------------------------------------------
# Grading & Analytics
# -----------------------------------------------------

class GradeBoundary(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)
    min_score = models.FloatField()
    max_score = models.FloatField()

    class Meta:
        unique_together = ('institution', 'subject', 'grade')
        ordering = ['-min_score']

    def __str__(self):
        return f"{self.grade}: {self.min_score}-{self.max_score}"


class ExamInsight(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='insights')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    average_score = models.FloatField()
    highest_score = models.FloatField()
    lowest_score = models.FloatField()
    most_common_grade = models.CharField(max_length=2)
    insight_summary = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insights - {self.exam} - {self.subject.name}"


# -----------------------------------------------------
# AI-Powered Predictions & Generation
# -----------------------------------------------------

class ExamPrediction(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    term = models.CharField(max_length=10, choices=Exam.TERM_CHOICES)
    year = models.PositiveIntegerField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    predicted_questions = models.JSONField()  # structured as list of dicts
    auto_generated_exam = models.TextField(blank=True)  # LaTeX or markdown format
    auto_generated_marking_scheme = models.TextField(blank=True)

    source_summary = models.TextField()  # sources used for prediction
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Predictions - {self.subject.name} ({self.term} {self.year})"
