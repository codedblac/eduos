from celery import shared_task
from django.utils import timezone
from events.models import Event
import datetime
from notifications.models import Notification
from accounts.models import CustomUser

@shared_task
def send_event_reminder_notifications():
    now = timezone.now()
    upcoming = now + datetime.timedelta(minutes=30)

    events = Event.objects.filter(start_time__range=(now, upcoming), is_active=True)

    for event in events:
        users = set()
        users.update(event.target_users.all())

        if event.target_roles:
            role_users = CustomUser.objects.filter(
                role__in=event.target_roles,
                institution=event.institution
            )
            users.update(role_users)

        notification = Notification.objects.create(
            institution=event.institution,
            title=f"Reminder: {event.title} in 30 minutes",
            message=f"Your event '{event.title}' starts at {event.start_time.strftime('%I:%M %p')}. Please be ready.",
            notification_type='event',
            created_by=None,
            target_users=list(users),
            target_roles=None,
            channels=["in_app", "sms"]
        )
