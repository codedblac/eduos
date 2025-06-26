from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.conf import settings
from institutions.models import Institution
from subjects.models import Subject, ClassLevel
from academics.models import Term 

User = settings.AUTH_USER_MODEL

# 1. Curriculum Framework (CBC, 8-4-4, IGCSE, etc.)
class Curriculum(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)  # Optional for national/global frameworks
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


# 2. Curriculum-Subject Link (by Class Level)
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


# 3. Syllabus Topic
class SyllabusTopic(models.Model):
    curriculum_subject = models.ForeignKey(CurriculumSubject, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    bloom_taxonomy_level = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=50, blank=True)  # easy, medium, hard
    estimated_duration_minutes = models.PositiveIntegerField(default=30)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# 4. Subtopics (Optional granularity)
class SyllabusSubtopic(models.Model):
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.CASCADE, related_name='subtopics')
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# 5. Learning Outcome
class LearningOutcome(models.Model):
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.CASCADE, related_name='outcomes')
    description = models.TextField()
    competency_area = models.CharField(max_length=255, blank=True)
    indicators = models.TextField(blank=True)  # comma-separated or structured JSON
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.description[:80]


# 6. Teaching Resources
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

    def __str__(self):
        return self.title


# 7. Syllabus Progress Tracking
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

    class Meta:
        unique_together = ('topic', 'teacher')

    def __str__(self):
        return f"{self.topic.title} - {self.status}"


# 8. Versioning
class SyllabusVersion(models.Model):
    curriculum_subject = models.ForeignKey(CurriculumSubject, on_delete=models.CASCADE)
    version_number = models.CharField(max_length=20)
    change_log = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.curriculum_subject} - v{self.version_number}"


# 9. Audit Log
class SyllabusAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    curriculum_subject = models.ForeignKey(CurriculumSubject, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} by {self.user}"
