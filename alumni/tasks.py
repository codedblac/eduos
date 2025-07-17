# alumni/tasks.py

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from .models import (
    AlumniNotification,
    AlumniFeedback,
    AlumniProfile,
    AlumniEvent,
    AlumniEventRegistration,
)
from notifications.utils import send_notification
from datetime import timedelta
from django.template.loader import render_to_string


@shared_task
def send_bulk_alumni_notification(title, message, institution_id, alumni_ids=None):
    """
    Send a notification to all or specific alumni.
    """
    qs = AlumniProfile.objects.filter(institution_id=institution_id)
    if alumni_ids:
        qs = qs.filter(id__in=alumni_ids)

    for alumni in qs:
        AlumniNotification.objects.create(
            title=title,
            message=message,
            recipient=alumni,
            institution_id=institution_id
        )
        # Optional: send email
        if alumni.email:
            send_mail(
                subject=title,
                message=message,
                from_email=None,
                recipient_list=[alumni.email],
                fail_silently=True,
            )


@shared_task
def send_event_reminders():
    """
    Automatically remind alumni of upcoming events 24 hours before.
    """
    upcoming_events = AlumniEvent.objects.filter(
        event_date=timezone.now().date() + timedelta(days=1)
    )

    for event in upcoming_events:
        registrations = AlumniEventRegistration.objects.filter(event=event)
        for reg in registrations:
            alumni = reg.alumni
            message = f"Reminder: You are registered for '{event.title}' happening on {event.event_date} at {event.location}."
            send_notification(
                institution=event.institution,
                users=[alumni.student.user],
                title="Event Reminder",
                message=message
            )


@shared_task
def auto_score_feedback():
    """
    Example task to analyze alumni feedback sentiment (placeholder logic).
    """
    feedbacks = AlumniFeedback.objects.filter(responded=False)
    for feedback in feedbacks:
        if 'bad' in feedback.message.lower():
            score = 'negative'
        elif 'good' in feedback.message.lower():
            score = 'positive'
        else:
            score = 'neutral'
        # Save or log this score
        print(f"[AI Feedback Score] Alumni {feedback.alumni.id}: {score}")


@shared_task
def cleanup_old_notifications():
    """
    Clean up notifications older than 6 months.
    """
    six_months_ago = timezone.now() - timedelta(days=180)
    AlumniNotification.objects.filter(sent_on__lt=six_months_ago).delete()
