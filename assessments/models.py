from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone

from academics.models import Term
from subjects.models import Subject
from classes.models import ClassLevel
from syllabus.models import SyllabusTopic, LearningOutcome
from institutions.models import Institution
from students.models import Student

User = settings.AUTH_USER_MODEL


class AssessmentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name



class AssessmentTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE)
    duration_minutes = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Assessment(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    type = models.ForeignKey(AssessmentType, on_delete=models.SET_NULL, null=True)
    template = models.ForeignKey(AssessmentTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('short', 'Short Answer'),
        ('essay', 'Essay'),
        ('code', 'Code'),
        ('match', 'Matching'),
        ('ordering', 'Ordering'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.SET_NULL, null=True, blank=True)
    outcome = models.ForeignKey(LearningOutcome, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    marks = models.PositiveIntegerField(default=1)
    difficulty_level = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"


class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class AssessmentSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_graded = models.BooleanField(default=False)
    is_adaptive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.assessment.title}"


class StudentAnswer(models.Model):
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(AnswerChoice, on_delete=models.SET_NULL, null=True, blank=True)
    written_answer = models.TextField(blank=True, null=True)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    auto_graded = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to {self.question}"  


class MarkingScheme(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    guide = models.TextField()
    rubric_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Marking for {self.question}"


class GradingRubric(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    criteria = models.CharField(max_length=255)
    max_score = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Rubric: {self.criteria}"


class Feedback(models.Model):
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Feedback by {self.created_by}"


class RetakePolicy(models.Model):
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE)
    max_attempts = models.PositiveIntegerField(default=1)
    wait_time_hours = models.PositiveIntegerField(default=24)
    allow_partial_retake = models.BooleanField(default=False)

    def __str__(self):
        return f"Retake Policy for {self.assessment.title}"
