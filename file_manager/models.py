import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from taggit.managers import TaggableManager
from institutions.models import Institution
from classes.models import ClassLevel, Stream
from subjects.models import Subject

User = settings.AUTH_USER_MODEL


class BaseTimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FileCategory(BaseTimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ManagedFile(BaseTimestampedModel):
    FILE_TYPES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('zip', 'ZIP Archive'),
        ('ebook', 'eBook'),
        ('report', 'Report'),
        ('assignment', 'Assignment'),
        ('lesson_note', 'Lesson Note'),
    ]

    ACCESS_SCOPE = [
        ('institution', 'Institution'),
        ('class', 'Class'),
        ('subject', 'Subject'),
        ('student', 'Student'),
        ('public', 'EduOS Global'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="file_manager/")
    file_size = models.PositiveBigIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=30, choices=FILE_TYPES)
    category = models.ForeignKey(FileCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_files')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_files')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_files')
    access_scope = models.CharField(max_length=30, choices=ACCESS_SCOPE, default='institution')
    is_public = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    compressed = models.BooleanField(default=False)
    preview_available = models.BooleanField(default=False)
    preview_url = models.URLField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    expires_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    is_recommended = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.name


class FileVersion(BaseTimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    managed_file = models.ForeignKey(ManagedFile, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to="file_manager/versions/")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changelog = models.TextField(blank=True)

    def __str__(self):
        return f"{self.managed_file.name} - v{self.version_number}"


class FileAccessLog(BaseTimestampedModel):
    ACTION_CHOICES = [
        ('viewed', 'Viewed'),
        ('downloaded', 'Downloaded'),
        ('deleted', 'Deleted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(ManagedFile, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    accessed_at = models.DateTimeField(auto_now_add=True)


class SharedAccess(BaseTimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(ManagedFile, on_delete=models.CASCADE, related_name='shared_access')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    can_download = models.BooleanField(default=True)
    can_comment = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    password_protected = models.BooleanField(default=False)


class AssignmentSubmission(BaseTimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(ManagedFile, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ('file', 'student')


class FileAnalytics(BaseTimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.OneToOneField(ManagedFile, on_delete=models.CASCADE, related_name='analytics')
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Analytics for {self.file.name}"


class FileComment(BaseTimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(ManagedFile, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"Comment by {self.user} on {self.file.name}"


class FileLock(models.Model):
    file = models.OneToOneField(ManagedFile, on_delete=models.CASCADE, related_name='lock')
    is_locked = models.BooleanField(default=False)
    locked_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    locked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.file.name} is {'locked' if self.is_locked else 'unlocked'}"
