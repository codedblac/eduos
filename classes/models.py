from django.db import models
from institutions.models import Institution

class ClassLevel(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='class_levels')
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('institution', 'name')
        ordering = ['order', 'name']
        verbose_name = 'Class Level'
        verbose_name_plural = 'Class Levels'

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


class Stream(models.Model):
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='streams')
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=20, unique=True)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('class_level', 'name')
        ordering = ['order', 'name']
        verbose_name = 'Stream'
        verbose_name_plural = 'Streams'

    def __str__(self):
        return f"{self.name} - {self.class_level.name}"
