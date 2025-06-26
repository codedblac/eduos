from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
from classes.models import ClassLevel, Stream
from accounts.models import CustomUser

User = settings.AUTH_USER_MODEL


class AnnouncementCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CommunicationAnnouncement(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    DELIVERY_CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements_created')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(AnnouncementCategory, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    channel = models.CharField(max_length=20, choices=DELIVERY_CHANNELS, default='in_app')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent = models.BooleanField(default=False)
    send_push = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_announcements")
    approved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="communications_created")
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="communications_updated")
    tags = models.CharField(max_length=255, blank=True)
    total_views = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["institution", "created_at"]),
            models.Index(fields=["scheduled_at"]),
            models.Index(fields=["sent"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.institution.name if self.institution else 'Public'})"


class AnnouncementAttachment(models.Model):
    announcement = models.ForeignKey(CommunicationAnnouncement, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='communications/attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class CommunicationTarget(models.Model):
    announcement = models.ForeignKey(CommunicationAnnouncement, on_delete=models.CASCADE, related_name='targets')
    role = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Target for {self.announcement}"


class CommunicationReadLog(models.Model):
    announcement = models.ForeignKey(CommunicationAnnouncement, on_delete=models.CASCADE, related_name='read_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('announcement', 'user')

    def __str__(self):
        return f"{self.user} read {self.announcement.title}"


class CommunicationLog(models.Model):
    announcement = models.ForeignKey(CommunicationAnnouncement, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.announcement.title} - {self.status} @ {self.timestamp}"
