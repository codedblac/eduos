# co_curricular/signals.py

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import (
    ActivityEvent,
    StudentActivityParticipation,
    TalentRecommendation,
    StudentAward
)
from notifications.utils import send_notification_to_user


@receiver(post_save, sender=StudentActivityParticipation)
def update_talent_profile_on_participation(sender, instance, created, **kwargs):
    """
    Update talent recommendations when participation changes.
    """
    student = instance.student
    recommendation, _ = TalentRecommendation.objects.get_or_create(student=student)
    participation_count = StudentActivityParticipation.objects.filter(student=student).count()
    recommendation.notes = f"Updated automatically based on {participation_count} participations."
    recommendation.recommended_date = now()
    recommendation.save()


@receiver(post_save, sender=StudentAward)
def notify_student_award(sender, instance, created, **kwargs):
    """
    Notify student when awarded.
    """
    if created:
        student = instance.student
        title = "🏅 Congratulations!"
        message = f"You have been awarded '{instance.title}' for your participation in {instance.activity.name}."
        send_notification_to_user(student.user, title, message)


@receiver(post_save, sender=ActivityEvent)
def notify_students_on_event_creation(sender, instance, created, **kwargs):
    """
    Notify related students when an event is created.
    """
    if created:
        # You can extend logic here if you store participants elsewhere
        message = f"A new event '{instance.name}' has been scheduled for {instance.start_date} at {instance.venue}."
        title = "New Co-Curricular Event"
        # If there's a way to get participants from the activity
        participants = StudentActivityParticipation.objects.filter(activity=instance.activity)
        for participation in participants:
            send_notification_to_user(participation.student.user, title, message)


@receiver(pre_delete, sender=ActivityEvent)
def notify_students_on_event_cancellation(sender, instance, **kwargs):
    """
    Notify students when an event is cancelled.
    """
    message = f"The event '{instance.name}' scheduled on {instance.start_date} has been cancelled."
    title = "Event Cancelled"
    participants = StudentActivityParticipation.objects.filter(activity=instance.activity)
    for participation in participants:
        send_notification_to_user(participation.student.user, title, message)
