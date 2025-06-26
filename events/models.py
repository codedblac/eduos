from django.db import models

# Create your models here.
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


class Event(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    location = models.CharField(max_length=255, blank=True)
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.URLField(blank=True, null=True)
    media_attachments = models.ManyToManyField('EventAttachment', blank=True)
    tags = models.ManyToManyField('EventTag', blank=True)

    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)

    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurring_rule = models.ForeignKey('RecurringEventRule', on_delete=models.SET_NULL, null=True, blank=True)

    # Targeting
    target_roles = models.JSONField(blank=True, null=True)  # e.g. ["teacher", "guardian"]
    target_users = models.ManyToManyField(User, blank=True, related_name='events_targeted')
    target_students = models.ManyToManyField(Student, blank=True)
    target_class_levels = models.ManyToManyField(ClassLevel, blank=True)
    target_streams = models.ManyToManyField(Stream, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='events_created')
    created_at = models.DateTimeField(auto_now_add=True)

    requires_rsvp = models.BooleanField(default=False)
    allow_feedback = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.start_time}"


class RecurringEventRule(models.Model):
    """
    Defines recurrence logic: daily, weekly, monthly, etc.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    interval = models.PositiveIntegerField(default=1)  # e.g. every 2 weeks
    end_date = models.DateField(blank=True, null=True)
    exceptions = models.JSONField(blank=True, null=True)  # dates to skip

    def __str__(self):
        return f"{self.frequency} every {self.interval}"


class EventAttachment(models.Model):
    file = models.FileField(upload_to='event_attachments/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class EventTag(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default="#000000")  # for frontend calendar color-coding

    def __str__(self):
        return self.name


class EventRSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No'), ('maybe', 'Maybe')])
    responded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'user')


class EventAttendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_present = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')


class EventFeedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
