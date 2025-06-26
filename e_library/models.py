from django.db import models
from django.conf import settings
from institutions.models import Institution
from classes.models import ClassLevel
from subjects.models import Subject
import uuid

RESOURCE_TYPES = [
    ('pdf', 'PDF'),
    ('video', 'Video'),
    ('audio', 'Audio'),
    ('presentation', 'Presentation'),
    ('external_link', 'External Link'),
]

VISIBILITY_CHOICES = [
    ('students', 'Students'),
    ('teachers', 'Teachers'),
    ('all', 'All Users'),
    ('institution', 'Institution Only'),
    ('public', 'Public'),
]

def resource_upload_path(instance, filename):
    # Path format: e_library/<institution_id>/<uploader_id>/<filename>
    return f"e_library/{instance.institution.id}/{instance.uploader.id}/{filename}"

class ELibraryCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "ELibrary Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class ELibraryTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class ELibraryResource(models.Model):
    """
    Core model for institution-level e-learning resources.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="e_library_resources")
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_resources')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to=resource_upload_path, blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='e_library_resources')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='e_library_resources')
    tags = models.ManyToManyField(ELibraryTag, blank=True, related_name='resources')
    category = models.ManyToManyField(ELibraryCategory, blank=True, related_name="resources")

    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='students')

    is_approved = models.BooleanField(default=False)
    auto_summary = models.TextField(blank=True, null=True)  # AI-generated summary
    ai_tags = models.TextField(blank=True, null=True)  # AI-generated tags (optional as text field for preview)

    recommended_for = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='recommended_resources'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['institution']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['visibility']),
        ]

    def __str__(self):
        return f"{self.title} ({self.institution.name})"

class ResourceViewLog(models.Model):
    """
    Tracks views/downloads of a resource.
    """
    resource = models.ForeignKey(ELibraryResource, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} viewed {self.resource.title} at {self.viewed_at}"

class ResourceVersion(models.Model):
    """
    Optional versioning of the same resource over time.
    """
    resource = models.ForeignKey(ELibraryResource, on_delete=models.CASCADE, related_name="versions")
    file = models.FileField(upload_to=resource_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Version of {self.resource.title} @ {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

