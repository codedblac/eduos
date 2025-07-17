from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from institutions.models import Institution
from students.models import Student
from classes.models import ClassLevel, Stream

User = get_user_model()
Role = User.Role


class EventType(models.TextChoices):
    ACADEMIC = 'academic', 'Academic'
    COCURRICULAR = 'cocurricular', 'Co-curricular'
    ADMINISTRATIVE = 'administrative', 'Administrative'
    PUBLIC = 'public', 'Public Holiday'
    VIRTUAL = 'virtual', 'Virtual Event'


class RecurringEventRule(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    interval = models.PositiveIntegerField(default=1)
    end_date = models.DateField(blank=True, null=True)
    exceptions = models.JSONField(blank=True, null=True)  # e.g. ["2025-08-15", ...]

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.frequency} every {self.interval}"


class EventTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=20, default="#000000")

    def __str__(self):
        return self.name


class EventAttachment(models.Model):
    file = models.FileField(upload_to='event_attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)


class Event(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=30, choices=EventType.choices)

    location = models.CharField(max_length=255, blank=True)
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.URLField(blank=True, null=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)

    is_recurring = models.BooleanField(default=False)
    recurring_rule = models.ForeignKey(RecurringEventRule, on_delete=models.SET_NULL, null=True, blank=True)

    tags = models.ManyToManyField(EventTag, blank=True)
    media_attachments = models.ManyToManyField(EventAttachment, blank=True)

    target_roles = models.JSONField(blank=True, null=True)
    target_users = models.ManyToManyField(User, blank=True, related_name='events_targeted')
    target_students = models.ManyToManyField(Student, blank=True)
    target_class_levels = models.ManyToManyField(ClassLevel, blank=True)
    target_streams = models.ManyToManyField(Stream, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='events_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    requires_rsvp = models.BooleanField(default=False)
    allow_feedback = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['institution', 'event_type', 'start_time']),
            models.Index(fields=['is_recurring', 'is_virtual'])
        ]

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def is_upcoming(self):
        return self.start_time > timezone.now()

    def is_ongoing(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class EventRSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No'), ('maybe', 'Maybe')])
    responded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-responded_at']


class EventAttendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_present = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="event_attendance_recorded")

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-timestamp']


class EventFeedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-submitted_at']


class EventComment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} on {self.event.title}: {self.comment[:30]}..."
