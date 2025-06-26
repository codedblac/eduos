from django.db import models
from django.utils import timezone
from django.conf import settings

from academics.models import Term
from subjects.models import Subject, ClassLevel
from syllabus.models import SyllabusTopic, SyllabusSubtopic

from institutions.models import Institution

User = settings.AUTH_USER_MODEL


class LessonPlan(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    topic = models.ForeignKey(SyllabusTopic, on_delete=models.SET_NULL, null=True)
    subtopic = models.ForeignKey(SyllabusSubtopic, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    objectives = models.TextField()
    teaching_method = models.CharField(
        max_length=50,
        choices=[
            ('lecture', 'Lecture'),
            ('discussion', 'Discussion'),
            ('practical', 'Practical'),
            ('digital', 'Digital'),
            ('hybrid', 'Hybrid')
        ]
    )
    delivery_mode = models.CharField(
        max_length=20,
        choices=[
            ('in_person', 'In-Person'),
            ('online', 'Online'),
            ('hybrid', 'Hybrid')
        ],
        default='in_person'
    )
    duration_minutes = models.PositiveIntegerField(default=40)
    resources = models.TextField(blank=True)
    week_number = models.PositiveIntegerField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('term', 'subject', 'class_level', 'teacher', 'topic', 'week_number')
        ordering = ['term', 'class_level', 'subject', 'week_number']

    def __str__(self):
        return f"LessonPlan: {self.subject.name} - {self.class_level.name} - Week {self.week_number}"


class LessonSchedule(models.Model):
    lesson_plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE, related_name='schedules')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    period = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('missed', 'Missed')
        ],
        default='scheduled'
    )

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']

    def __str__(self):
        return f"{self.lesson_plan} on {self.scheduled_date}"


class LessonSession(models.Model):
    lesson_schedule = models.OneToOneField(LessonSchedule, on_delete=models.CASCADE, related_name='session')
    delivered_on = models.DateField(default=timezone.now)
    summary = models.TextField(blank=True)
    coverage_status = models.CharField(
        max_length=20,
        choices=[
            ('covered', 'Covered'),
            ('postponed', 'Postponed'),
            ('cancelled', 'Cancelled'),
            ('skipped', 'Skipped')
        ],
        default='covered'
    )
    homework = models.TextField(blank=True)
    challenges_faced = models.TextField(blank=True)
    is_reviewed = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lesson_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-delivered_on']

    def __str__(self):
        return f"{self.lesson_schedule.lesson_plan.subject.name} - {self.delivered_on}"


class LessonAttachment(models.Model):
    lesson_session = models.ForeignKey(LessonSession, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='lesson_files/', null=True, blank=True)
    external_link = models.URLField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
