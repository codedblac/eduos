from celery import shared_task
from django.utils import timezone
from .models import Event, EventRSVP, EventFeedback
from notifications.models import Notification
from accounts.models import CustomUser


@shared_task
def send_event_reminders():
    """
    Send reminders for events starting in the next hour.
    """
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        is_active=True,
        start_time__range=[now, now + timezone.timedelta(hours=1)]
    )

    for event in upcoming_events:
        users = event.target_users.all()
        for user in users:
            Notification.objects.create(
                institution=event.institution,
                title=f"Upcoming Event: {event.title}",
                message=f"Reminder: {event.title} starts at {event.start_time.strftime('%H:%M')}",
                notification_type="event_reminder",
                created_by=event.created_by,
                is_active=True,
            ).target_users.add(user)


@shared_task
def archive_past_events():
    """
    Automatically deactivate past events that have ended more than 30 days ago.
    """
    threshold = timezone.now() - timezone.timedelta(days=30)
    old_events = Event.objects.filter(end_time__lt=threshold, is_active=True)
    count = old_events.update(is_active=False)
    return f"{count} events archived."


@shared_task
def auto_collect_event_feedback():
    """
    Send feedback requests for recently ended events.
    """
    now = timezone.now()
    recent_events = Event.objects.filter(
        allow_feedback=True,
        end_time__range=[now - timezone.timedelta(hours=1), now],
        is_active=True
    )

    for event in recent_events:
        users = event.target_users.all()
        for user in users:
            if not EventFeedback.objects.filter(event=event, user=user).exists():
                Notification.objects.create(
                    institution=event.institution,
                    title=f"Feedback Requested: {event.title}",
                    message="We value your opinion! Please share feedback for the recent event.",
                    notification_type="event_feedback",
                    created_by=event.created_by,
                    is_active=True,
                ).target_users.add(user)


@shared_task
def send_rsvp_reminders():
    """
    Remind users who haven't RSVP'd to upcoming events.
    """
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        requires_rsvp=True,
        start_time__gt=now,
        is_active=True
    )

    for event in upcoming_events:
        target_users = event.target_users.all()
        rsvp_users = EventRSVP.objects.filter(event=event).values_list('user_id', flat=True)
        pending_users = target_users.exclude(id__in=rsvp_users)

        for user in pending_users:
            Notification.objects.create(
                institution=event.institution,
                title=f"RSVP Needed: {event.title}",
                message="Please confirm your attendance for the upcoming event.",
                notification_type="event_rsvp_reminder",
                created_by=None,
                is_active=True,
            ).target_users.add(user)
