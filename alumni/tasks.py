from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum

from .models import (
    AlumniEvent,
    AlumniContribution,
    AlumniAnnouncement,
    AlumniProfile
)

from accounts.models import CustomUser


def notify_upcoming_alumni_events():
    """
    Send email reminders to alumni for events happening within 3 days.
    """
    upcoming_events = AlumniEvent.objects.filter(
        event_date__range=[timezone.now(), timezone.now() + timedelta(days=3)]
    )

    for event in upcoming_events:
        alumni_users = CustomUser.objects.filter(groups__name='alumni')
        for user in alumni_users:
            send_mail(
                subject=f"Upcoming Alumni Event: {event.title}",
                message=f"Dear {user.first_name},\n\nDon't miss our upcoming event: {event.title} on {event.event_date.date()} at {event.location}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )


def summarize_monthly_contributions():
    """
    Compute and log monthly contribution summaries for analytics.
    """
    from .analytics import AlumniAnalyticsEngine

    summary = AlumniContribution.objects.filter(
        date_contributed__month=timezone.now().month
    ).aggregate(total=Sum('amount'))

    AlumniAnalyticsEngine.log_monthly_contribution_summary(
        amount=summary['total'] or 0,
        month=timezone.now().strftime('%B')
    )


def send_announcement_to_all_alumni(announcement_id):
    """
    Send a specific announcement to all alumni.
    """
    try:
        announcement = AlumniAnnouncement.objects.get(id=announcement_id)
        alumni_users = CustomUser.objects.filter(groups__name='alumni')

        for user in alumni_users:
            send_mail(
                subject=announcement.title,
                message=announcement.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
    except AlumniAnnouncement.DoesNotExist:
        pass


def send_welcome_email_to_new_alumni(alumni_id):
    """
    Welcome email when a new alumni profile is created.
    """
    try:
        alumni = AlumniProfile.objects.get(id=alumni_id)
        user = alumni.user

        send_mail(
            subject="Welcome to the Alumni Network",
            message=f"Dear {user.first_name},\n\nWelcome to the Alumni Network of {alumni.institution.name}. Stay connected and make a difference!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except AlumniProfile.DoesNotExist:
        pass
