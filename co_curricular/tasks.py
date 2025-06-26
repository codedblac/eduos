# co_curricular/tasks.py

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from .models import CoCurricularEvent, StudentParticipation, TalentProfile
from notifications.utils import send_notification_to_user
from accounts.models import CustomUser


@shared_task
def notify_upcoming_events():
    """
    Sends notifications to users about co-curricular events scheduled within the next 24 hours.
    """
    now = timezone.now()
    upcoming = CoCurricularEvent.objects.filter(
        start_datetime__range=[now, now + timedelta(hours=24)],
        is_cancelled=False
    )

    for event in upcoming:
        for student in event.participants.all():
            user = student.user
            message = f"You have a {event.name} scheduled on {event.start_datetime.strftime('%d %b %Y %I:%M %p')}."
            send_notification_to_user(user, f"Upcoming Activity: {event.name}", message)


@shared_task
def weekly_participation_digest():
    """
    Sends weekly summary to activity heads detailing participation logs and missed sessions.
    """
    last_week = timezone.now() - timedelta(days=7)
    activity_heads = CustomUser.objects.filter(groups__name='ActivityHead')

    for head in activity_heads:
        activities = StudentParticipation.objects.filter(
            event__activity_head=head,
            attended=False,
            event__start_datetime__gte=last_week
        )
        missed_count = activities.count()

        if missed_count > 0:
            msg = f"You had {missed_count} missed participation logs this week for your activities."
            send_notification_to_user(head, "Weekly Activity Digest", msg)


@shared_task
def update_talent_profiles():
    """
    Refreshes TalentProfile ratings based on most recent activity performance records.
    """
    profiles = TalentProfile.objects.all()

    for profile in profiles:
        participations = StudentParticipation.objects.filter(student=profile.student)
        awards = participations.filter(award__isnull=False).count()
        total = participations.count()

        profile.participation_count = total
        profile.awards_count = awards
        profile.engagement_score = min(100, (awards * 10 + total * 2))  # Simple scoring formula
        profile.save()


@shared_task
def send_event_feedback_requests():
    """
    After an event is completed, send feedback requests to participants (if enabled).
    """
    past_events = CoCurricularEvent.objects.filter(
        end_datetime__lt=timezone.now(),
        feedback_enabled=True,
        feedback_sent=False
    )

    for event in past_events:
        for student in event.participants.all():
            msg = f"Please provide feedback for the {event.name} held on {event.start_datetime.strftime('%d %b')}."
            send_notification_to_user(student.user, "We value your feedback", msg)

        event.feedback_sent = True
        event.save()


@shared_task
def auto_archive_old_events():
    """
    Archives events older than a year to optimize performance.
    """
    one_year_ago = timezone.now() - timedelta(days=365)
    old_events = CoCurricularEvent.objects.filter(start_datetime__lt=one_year_ago, is_archived=False)

    for event in old_events:
        event.is_archived = True
        event.save()
