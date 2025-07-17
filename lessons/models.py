from django.db import models
from django.utils import timezone
from django.conf import settings

from institutions.models import Institution
from academics.models import Term
from subjects.models import Subject, ClassLevel
from syllabus.models import SyllabusTopic, SyllabusSubtopic

User = settings.AUTH_USER_MODEL


class LessonPlan(models.Model):
    """
    A teacher's plan for a lesson (not yet delivered).
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.SET_NULL, null=True, blank=True)
    subtopic = models.ForeignKey(SyllabusSubtopic, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    objectives = models.TextField()
    activities = models.TextField(blank=True)
    assessments = models.TextField(blank=True)

    teaching_method = models.CharField(
        max_length=50,
        choices=[
            ('lecture', 'Lecture'),
            ('discussion', 'Discussion'),
            ('practical', 'Practical'),
            ('digital', 'Digital'),
            ('hybrid', 'Hybrid')
        ],
        default='lecture'
    )
    delivery_mode = models.CharField(
        max_length=20,
        choices=[
            ('in_person', 'In-Person'),
            ('online', 'Online'),
            ('hybrid', 'Hybrid')
        ],
        default='in_person'
    )

    duration_minutes = models.PositiveIntegerField(default=40)
    resources = models.TextField(blank=True)
    week_number = models.PositiveIntegerField()

    is_approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lesson_reviews')
    approved_at = models.DateTimeField(null=True, blank=True)

    version = models.PositiveIntegerField(default=1)
    is_draft = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('term', 'subject', 'class_level', 'teacher', 'topic', 'week_number')
        ordering = ['term', 'class_level', 'subject', 'week_number']

    def __str__(self):
        return f"LessonPlan: {self.subject.name} - {self.class_level.name} - Week {self.week_number}"


class LessonSchedule(models.Model):
    """
    When a lesson is expected to happen.
    """
    lesson_plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE, related_name='schedules')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    period = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('missed', 'Missed'),
            ('cancelled', 'Cancelled')
        ],
        default='scheduled'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']

    def __str__(self):
        return f"{self.lesson_plan.subject.name} - {self.scheduled_date} {self.scheduled_time}"


class LessonSession(models.Model):
    """
    Actual lesson delivery session with outcomes.
    """
    lesson_schedule = models.OneToOneField(LessonSchedule, on_delete=models.CASCADE, related_name='session')
    delivered_on = models.DateField(default=timezone.now)
    summary = models.TextField(blank=True)
    coverage_status = models.CharField(
        max_length=20,
        choices=[
            ('covered', 'Covered'),
            ('partial', 'Partially Covered'),
            ('postponed', 'Postponed'),
            ('cancelled', 'Cancelled'),
            ('skipped', 'Skipped')
        ],
        default='covered'
    )
    homework = models.TextField(blank=True)
    student_engagement_notes = models.TextField(blank=True)
    challenges_faced = models.TextField(blank=True)
    teacher_reflection = models.TextField(blank=True)

    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='session_reviews')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lesson_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-delivered_on']

    def __str__(self):
        return f"{self.lesson_schedule.lesson_plan.subject.name} - {self.delivered_on}"


class LessonAttachment(models.Model):
    """
    Attached files or links used during the lesson.
    """
    lesson_session = models.ForeignKey(LessonSession, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='lesson_files/', null=True, blank=True)
    external_link = models.URLField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class LessonFeedback(models.Model):
    """
    Feedback from student or supervisor about a lesson.
    """
    lesson_session = models.ForeignKey(LessonSession, on_delete=models.CASCADE, related_name='feedbacks')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=20, choices=[('student', 'Student'), ('peer', 'Peer'), ('supervisor', 'Supervisor')])
    rating = models.PositiveIntegerField(null=True, blank=True)
    comment = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback ({self.role}) - {self.lesson_session}"


class LessonTemplate(models.Model):
    """
    Optional reusable lesson templates to auto-generate lesson plans.
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.SET_NULL, null=True, blank=True)
    subtopic = models.ForeignKey(SyllabusSubtopic, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    objectives = models.TextField()
    activities = models.TextField(blank=True)
    assessments = models.TextField(blank=True)
    teaching_method = models.CharField(max_length=50)
    delivery_mode = models.CharField(max_length=20, default='in_person')
    recommended_duration = models.PositiveIntegerField(default=40)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Template: {self.title} ({self.subject.name})"


class LessonScaffoldSuggestion(models.Model):
    lesson = models.ForeignKey(
        "lessons.LessonPlan",  
        on_delete=models.CASCADE,
        related_name="scaffold_suggestions"
    )
    suggestion = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suggestion for {self.lesson} by {self.created_by}"