from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from .models import (
    ActivityEvent,
    StudentActivityParticipation,
    StudentProfile,
    CoachFeedback,
    ActivityPerformance
)
from notifications.utils import send_notification_to_user
from accounts.models import CustomUser


@shared_task
def notify_upcoming_events():
    """
    Sends notifications to users about co-curricular events scheduled within the next 24 hours.
    """
    now = timezone.now()
    upcoming = ActivityEvent.objects.filter(
        start_date__range=[now.date(), (now + timedelta(days=1)).date()]
    )

    for event in upcoming:
        participants = StudentActivityParticipation.objects.filter(activity=event.activity, is_active=True)
        for participation in participants:
            student = participation.student
            if student.user:
                message = f"You have '{event.name}' scheduled for {event.start_date} at {event.venue}."
                send_notification_to_user(student.user, f"Upcoming Activity: {event.name}", message)


@shared_task
def weekly_participation_digest():
    """
    Sends weekly summary to coaches or patrons detailing participation logs.
    """
    last_week = timezone.now() - timedelta(days=7)
    heads = CustomUser.objects.filter(groups__name='ActivityHead')

    for head in heads:
        activities_led = StudentActivityParticipation.objects.filter(
            activity__coach_or_patron=head,
            joined_on__gte=last_week
        )
        participation_count = activities_led.count()
        if participation_count > 0:
            msg = f"You have {participation_count} new participations recorded this past week."
            send_notification_to_user(head, "Weekly Participation Summary", msg)


@shared_task
def update_talent_profiles():
    """
    Refreshes StudentProfile participation/award scores based on latest activity.
    """
    profiles = StudentProfile.objects.all()

    for profile in profiles:
        participations = StudentActivityParticipation.objects.filter(student=profile.student)
        total = participations.count()
        awards = profile.student.studentaward_set.count()

        profile.participation_count = total
        profile.awards_count = awards
        profile.engagement_score = min(100, (total * 2 + awards * 10))  # Adjustable formula
        profile.save()


@shared_task
def send_event_feedback_requests():
    """
    After an event ends, request feedback from participants if enabled.
    """
    today = timezone.now().date()
    past_events = ActivityEvent.objects.filter(
        end_date__lt=today,
        activity__is_active=True,
        activity__is_competitive=True  # Assuming feedback is needed for competitive activities
    )

    for event in past_events:
        participants = StudentActivityParticipation.objects.filter(activity=event.activity)
        for participation in participants:
            student = participation.student
            if student.user:
                msg = f"Kindly provide feedback for '{event.name}' held on {event.start_date}."
                send_notification_to_user(student.user, "We Value Your Feedback", msg)


@shared_task
def auto_archive_old_events():
    """
    Archives events older than 1 year to reduce clutter.
    """
    one_year_ago = timezone.now().date() - timedelta(days=365)
    old_events = ActivityEvent.objects.filter(start_date__lt=one_year_ago)

    for event in old_events:
        event.activity.is_active = False
        event.activity.save()
