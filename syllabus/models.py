from django.db import models
from django.utils import timezone
from django.conf import settings
from institutions.models import Institution
from subjects.models import Subject, ClassLevel
from academics.models import Term

User = settings.AUTH_USER_MODEL


class Curriculum(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class CurriculumSubject(models.Model):
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('curriculum', 'subject', 'class_level', 'term')
        ordering = ['class_level', 'term', 'ordering']

    def __str__(self):
        return f"{self.subject.name} - {self.class_level.name} - {self.term.name}"


class SyllabusTopic(models.Model):
    curriculum_subject = models.ForeignKey(CurriculumSubject, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    bloom_taxonomy_level = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=50, blank=True)
    difficulty_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estimated_duration_minutes = models.PositiveIntegerField(default=30)
    order = models.PositiveIntegerField(default=0)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_topics')
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_topics')
    approved_at = models.DateTimeField(null=True, blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependents')
    ai_summary = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class SyllabusSubtopic(models.Model):
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.CASCADE, related_name='subtopics')
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class LearningOutcome(models.Model):
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.CASCADE, related_name='outcomes')
    description = models.TextField()
    competency_area = models.CharField(max_length=255, blank=True)
    indicators = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.description[:80]


class TeachingResource(models.Model):
    subtopic = models.ForeignKey(SyllabusSubtopic, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE, related_name='resources', null=True, blank=True)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=[
        ('document', 'Document'),
        ('video', 'Video'),
        ('link', 'Link'),
        ('interactive', 'Interactive')
    ])
    file = models.FileField(upload_to='syllabus/resources/', blank=True, null=True)
    url = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    last_viewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class SyllabusProgress(models.Model):
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('covered', 'Covered'),
        ('skipped', 'Skipped')
    ], default='pending')
    coverage_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('topic', 'teacher')

    def __str__(self):
        return f"{self.topic.title} - {self.status}"


class SyllabusVersion(models.Model):
    curriculum_subject = models.ForeignKey(CurriculumSubject, on_delete=models.CASCADE)
    version_number = models.CharField(max_length=20)
    change_log = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.curriculum_subject} - v{self.version_number}"


class SyllabusAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    curriculum_subject = models.ForeignKey(CurriculumSubject, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} by {self.user}"
