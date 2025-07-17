# alumni/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    AlumniProfile,
    AlumniEventRegistration,
    AlumniFeedback,
    AlumniMentorship,
    AlumniNotification
)
from .tasks import (
    send_bulk_alumni_notification,
    auto_score_feedback,
)
from notifications.utils import send_notification
from django.core.mail import send_mail


@receiver(post_save, sender=AlumniProfile)
def handle_new_alumni_profile(sender, instance, created, **kwargs):
    if created:
        # Send welcome notification and email
        send_notification(
            institution=instance.institution,
            users=[instance.student.user],
            title="Welcome to the Alumni Network!",
            message=f"Hi {instance.student.full_name()}, your alumni profile has been created successfully."
        )
        if instance.email:
            send_mail(
                subject="Welcome to the Alumni Network",
                message="Thank you for joining our alumni community. Stay connected!",
                from_email=None,
                recipient_list=[instance.email],
                fail_silently=True,
            )


@receiver(post_save, sender=AlumniEventRegistration)
def notify_event_registration(sender, instance, created, **kwargs):
    if created:
        message = f"Hi {instance.alumni.student.full_name()}, you have successfully registered for the event: '{instance.event.title}' scheduled on {instance.event.event_date}."
        send_notification(
            institution=instance.event.institution,
            users=[instance.alumni.student.user],
            title="Event Registration Successful",
            message=message
        )


@receiver(post_save, sender=AlumniFeedback)
def trigger_feedback_analysis(sender, instance, created, **kwargs):
    if created:
        auto_score_feedback.delay()


@receiver(post_save, sender=AlumniMentorship)
def notify_new_mentorship(sender, instance, created, **kwargs):
    if created:
        mentor_user = instance.mentor.student.user
        mentee_user = instance.mentee.user
        # Notify both mentor and mentee
        send_notification(
            institution=instance.institution,
            users=[mentor_user],
            title="New Mentee Assigned",
            message=f"You have been assigned to mentor {instance.mentee.full_name()}."
        )
        send_notification(
            institution=instance.institution,
            users=[mentee_user],
            title="New Mentor Assigned",
            message=f"You have been assigned {instance.mentor.student.full_name()} as your mentor."
        )
