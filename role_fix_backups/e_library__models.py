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
    is_rejected = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_e_library_resources')
    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='rejected_e_library_resources')
    approval_comment = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    auto_summary = models.TextField(blank=True, null=True)
    ai_tags = models.TextField(blank=True, null=True)

    recommended_for = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='recommended_resources')

    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    language = models.CharField(max_length=50, default='English')
    license_type = models.CharField(max_length=50, blank=True, null=True)
    copyright_holder = models.CharField(max_length=255, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields = ['institution']),
            models.Index(fields = ['resource_type']),
            models.Index(fields = ['visibility']),
        ]

    def __str__(self):
        return f"{self.title} ({self.institution.name})"

class ResourceViewLog(models.Model):
    resource = models.ForeignKey(ELibraryResource, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    action = models.CharField(max_length=20, choices=[('view', 'View'), ('download', 'Download')], default='view')

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} {self.action}ed {self.resource.title}"

class ResourceVersion(models.Model):
    resource = models.ForeignKey(ELibraryResource, on_delete=models.CASCADE, related_name="versions")
    file = models.FileField(upload_to=resource_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Version of {self.resource.title} @ {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

class ResourceRating(models.Model):
    resource = models.ForeignKey(ELibraryResource, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('resource', 'user')

    def __str__(self):
        return f"{self.resource.title} rated {self.rating} by {self.user.username}"

class AIAssistedEdit(models.Model):
    resource = models.ForeignKey(ELibraryResource, on_delete=models.CASCADE, related_name='ai_logs')
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField()
    tags_added = models.TextField(blank=True)
    generated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Edit on {self.resource.title} by {self.performed_by}"
