from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from institutions.models import Institution
from students.models import Student
from classes.models import ClassLevel, Stream  


User = get_user_model()
Role = User.Role

class NotificationChannel(models.TextChoices):
    EMAIL = 'email', 'Email'
    SMS = 'sms', 'SMS'
    PUSH = 'push', 'Push Notification'
    IN_APP = 'in_app', 'In-App'


class NotificationType(models.TextChoices):
    GENERAL = 'general', 'General Announcement'
    MEDICAL = 'medical', 'Medical Alert'
    EXAM = 'exam', 'Exam Update'
    FEE = 'fee', 'Fee Alert'
    TIMETABLE = 'timetable', 'Timetable Change'
    LIBRARY = 'library', 'Library Notice'
    CUSTOM = 'custom', 'Custom'


class Notification(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.GENERAL)
    channels = models.JSONField(default=list)  # e.g. ["sms", "email"]

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notifications_sent')
    created_at = models.DateTimeField(default=timezone.now)

    # Targeting
    target_roles = models.JSONField(blank=True, null=True)  # e.g. ["teacher", "guardian"]
    target_users = models.ManyToManyField(User, blank=True, related_name='targeted_notifications')
    target_students = models.ManyToManyField(Student, blank=True)
    target_class_levels = models.ManyToManyField(ClassLevel, blank=True)
    target_streams = models.ManyToManyField(Stream, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.notification_type}"


class NotificationDelivery(models.Model):
    """
    Each individual delivery instance (1 per user per channel per notification)
    """
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    delivered = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.channel} - {self.notification.title}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allow_email = models.BooleanField(default=True)
    allow_sms = models.BooleanField(default=True)
    allow_push = models.BooleanField(default=True)
    allow_in_app = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferences - {self.user}"
