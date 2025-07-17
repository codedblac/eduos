from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import (
    ActivityEvent,
    StudentActivityParticipation,
    TalentRecommendation,
    StudentAward,
    StudentProfile,
    CoachFeedback,
)
from notifications.utils import send_notification_to_user


@receiver(post_save, sender=StudentActivityParticipation)
def update_student_profile_and_recommendation(sender, instance, created, **kwargs):
    """
    Auto-create or update the student's profile and talent recommendation when they participate.
    """
    student = instance.student

    # Ensure StudentProfile exists
    profile, _ = StudentProfile.objects.get_or_create(student=student)

    # Optionally update skill level summary
    participations = StudentActivityParticipation.objects.filter(student=student)
    total = participations.count()
    profile.last_participation_count = total
    profile.updated_at = now()
    profile.save()

    # Update/create a general talent recommendation
    recommendation, _ = TalentRecommendation.objects.get_or_create(student=student)
    recommendation.notes = f"Auto-updated: {total} participations as of {now().strftime('%Y-%m-%d')}."
    recommendation.recommended_date = now()
    recommendation.save()


@receiver(post_save, sender=StudentAward)
def notify_student_award(sender, instance, created, **kwargs):
    """
    Notify student when awarded.
    """
    if created and instance.student.user:
        student_user = instance.student.user
        title = "🏅 Congratulations!"
        message = f"You have been awarded '{instance.title}' for your participation in {instance.activity.name}."
        send_notification_to_user(student_user, title, message)


@receiver(post_save, sender=ActivityEvent)
def notify_students_on_event_creation(sender, instance, created, **kwargs):
    """
    Notify participants when an event is created.
    """
    if created:
        title = "📅 New Co-Curricular Event"
        message = (
            f"A new event '{instance.name}' has been scheduled for {instance.start_date} "
            f"at {instance.venue} under {instance.activity.name}."
        )
        participants = StudentActivityParticipation.objects.filter(activity=instance.activity)
        for participation in participants:
            if participation.student.user:
                send_notification_to_user(participation.student.user, title, message)


@receiver(pre_delete, sender=ActivityEvent)
def notify_students_on_event_cancellation(sender, instance, **kwargs):
    """
    Notify participants when an event is cancelled.
    """
    title = "❌ Event Cancelled"
    message = (
        f"The event '{instance.name}' scheduled on {instance.start_date} for {instance.activity.name} has been cancelled."
    )
    participants = StudentActivityParticipation.objects.filter(activity=instance.activity)
    for participation in participants:
        if participation.student.user:
            send_notification_to_user(participation.student.user, title, message)


@receiver(post_save, sender=CoachFeedback)
def notify_student_coach_feedback(sender, instance, created, **kwargs):
    """
    Notify student when coach submits feedback.
    """
    if created and instance.participation.student.user:
        title = "📝 Coach Feedback Received"
        message = (
            f"Your coach {instance.coach} left feedback on your participation in "
            f"{instance.participation.activity.name}."
        )
        send_notification_to_user(instance.participation.student.user, title, message)
