from django.db import models
from institutions.models import Institution
from classes.models import ClassLevel
from teachers.models import Teacher


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_elective = models.BooleanField(default=False)
    is_core = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='subjects')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='subject_links'  
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teacher_links'  
    )

    class Meta:
        unique_together = ('teacher', 'subject')

    def __str__(self):
        return f"{self.teacher} - {self.subject}"


