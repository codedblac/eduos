from django.db import models
from django.utils import timezone
from institutions.models import Institution
from classes.models import ClassLevel
from teachers.models import Teacher
from academics.models import Term
from accounts.models import CustomUser


class SubjectCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    CURRICULUM_CHOICES = [
        ("CBC", "CBC"),
        ("IGCSE", "IGCSE"),
        ("KCSE", "KCSE"),
        ("IB", "IB"),
        ("Custom", "Custom"),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_elective = models.BooleanField(default=False)
    is_core = models.BooleanField(default=False)
    category = models.ForeignKey(SubjectCategory, on_delete=models.SET_NULL, null=True, blank=True)
    curriculum_type = models.CharField(max_length=50, choices=CURRICULUM_CHOICES, default="CBC")
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('name', 'institution')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class SubjectClassLevel(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_levels')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='subjects')
    compulsory = models.BooleanField(default=False)

    class Meta:
        unique_together = ('subject', 'class_level')

    def __str__(self):
        return f"{self.subject.name} - {self.class_level.name}"


class SubjectTeacher(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_links')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='subject_links')
    is_head = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'subject')

    def __str__(self):
        return f"{self.teacher} - {self.subject}"


class SubjectPrerequisite(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='main_subject')
    prerequisite = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='prerequisites')
    is_corequisite = models.BooleanField(default=False)

    class Meta:
        unique_together = ('subject', 'prerequisite')

    def __str__(self):
        return f"{self.prerequisite} -> {self.subject}"


class SubjectAssessmentWeight(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assessment_weights')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='subject_weights')
    component = models.CharField(max_length=100)  # e.g., CAT, Exam, Project
    weight_percentage = models.PositiveIntegerField()

    class Meta:
        unique_together = ('subject', 'term', 'component')

    def __str__(self):
        return f"{self.subject.name} - {self.component} ({self.weight_percentage}%)"


class SubjectGradingScheme(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grading_schemes')
    grade = models.CharField(max_length=5)
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('subject', 'grade')
        ordering = ['-max_score']

    def __str__(self):
        return f"{self.subject.name}: {self.grade} ({self.min_score}-{self.max_score})"


class SubjectResource(models.Model):
    RESOURCE_TYPES = [
        ('document', 'Document'),
        ('video', 'Video'),
        ('interactive', 'Interactive'),
        ('link', 'Link'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='subjects/resources/', null=True, blank=True)
    url = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SubjectVersion(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20)
    changelog = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subject', 'version_number')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject.name} v{self.version_number}"


class SubjectAnalyticsLog(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='analytics_logs')
    average_score = models.DecimalField(max_digits=5, decimal_places=2)
    highest_score = models.DecimalField(max_digits=5, decimal_places=2)
    lowest_score = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-recorded_at']
        verbose_name = "Subject Analytics Log"
        verbose_name_plural = "Subject Analytics Logs"

    def __str__(self):
        return f"{self.subject.name} Analytics @ {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"
