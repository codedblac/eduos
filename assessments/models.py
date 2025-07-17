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
    type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name="templates")
    duration_minutes = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AssessmentGroup(models.Model):
    name = models.CharField(max_length=255)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="assessment_groups")
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="assessment_groups")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_assessment_groups")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.term.name})"


class Assessment(models.Model):
    DELIVERY_MODE_CHOICES = [
        ('online', 'Online'),
        ('print', 'Printed'),
        ('hybrid', 'Hybrid'),
    ]

    CREATION_METHOD_CHOICES = [
        ('manual', 'Manual'),
        ('auto', 'Auto'),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="assessments")
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assessments")
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name="assessments")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="assessments")
    type = models.ForeignKey(AssessmentType, on_delete=models.SET_NULL, null=True, related_name="assessments")
    template = models.ForeignKey(AssessmentTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="used_in_assessments")
    group = models.ForeignKey(AssessmentGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="assessments")
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_assessments")
    created_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    creation_method = models.CharField(max_length=20, choices=CREATION_METHOD_CHOICES, default='manual')
    delivery_mode = models.CharField(max_length=20, choices=DELIVERY_MODE_CHOICES, default='online')
    is_recurring = models.BooleanField(default=False)
    recurrence_interval_days = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"


class AssessmentWeight(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="assessment_weights")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assessment_weights_assessments")  # <-- Changed
    type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name="weights")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="assessment_weights")
    weight = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ('institution', 'subject', 'term', 'type')



class AssessmentLock(models.Model):
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name="lock")
    locked = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)


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
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    outcome = models.ForeignKey(LearningOutcome, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    text = models.TextField()
    type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    marks = models.PositiveIntegerField(default=1)
    difficulty_level = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"


class CodeTestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="test_cases", limit_choices_to={'type': 'code'})
    input_data = models.TextField()
    expected_output = models.TextField()
    weight = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Test Case for Q{self.question.id}"


class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class AssessmentSession(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="assessment_sessions")
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="sessions")
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="graded_sessions")
    is_graded = models.BooleanField(default=False)
    is_adaptive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.assessment.title}"


class AssessmentVisibility(models.Model):
    session = models.OneToOneField(AssessmentSession, on_delete=models.CASCADE, related_name="visibility")
    can_view_score = models.BooleanField(default=False)
    can_view_feedback = models.BooleanField(default=False)
    released_at = models.DateTimeField(null=True, blank=True)


class StudentAnswer(models.Model):
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    selected_choice = models.ForeignKey(AnswerChoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="selected_by")
    written_answer = models.TextField(blank=True, null=True)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    auto_graded = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to {self.question}"  


class MarkingScheme(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name="marking_scheme")
    guide = models.TextField()
    rubric_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Marking for {self.question}"


class GradingRubric(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="rubrics")
    criteria = models.CharField(max_length=255)
    max_score = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Rubric: {self.criteria}"


class Feedback(models.Model):
    session = models.ForeignKey(AssessmentSession, on_delete=models.CASCADE, related_name="feedback")
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="given_feedback")

    def __str__(self):
        return f"Feedback by {self.created_by}"


class RetakePolicy(models.Model):
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name="retake_policy")
    max_attempts = models.PositiveIntegerField(default=1)
    wait_time_hours = models.PositiveIntegerField(default=24)
    allow_partial_retake = models.BooleanField(default=False)

    def __str__(self):
        return f"Retake Policy for {self.assessment.title}"


class PerformanceTrend(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="performance_trends")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="performance_trends")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="performance_trends")
    average_score = models.DecimalField(max_digits=5, decimal_places=2)
    assessment_count = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Trend - {self.student} - {self.subject}"


class AssessmentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.assessment} - {self.score}"