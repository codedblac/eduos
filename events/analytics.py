from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import Event, EventRSVP, EventAttendance, EventFeedback


def get_event_type_distribution(institution):
    """
    Returns a breakdown of event counts per type for the given institution.
    """
    return (
        Event.objects.filter(institution=institution)
        .values('event_type')
        .annotate(total=Count('id'))
        .order_by('-total')
    )


def get_upcoming_event_count(institution, days=7):
    """
    Returns the number of upcoming events in the next 'days' for the institution.
    """
    now = timezone.now()
    future = now + timedelta(days=days)
    return Event.objects.filter(institution=institution, start_time__range=(now, future)).count()


def get_rsvp_summary(event):
    """
    Returns RSVP response counts for a given event.
    """
    return (
        EventRSVP.objects.filter(event=event)
        .values('response')
        .annotate(count=Count('id'))
    )


def get_attendance_rate(event):
    """
    Returns attendance statistics for a given event.
    """
    total_invited = event.target_users.count()
    total_responded = EventAttendance.objects.filter(event=event).count()
    total_present = EventAttendance.objects.filter(event=event, is_present=True).count()

    return {
        "invited": total_invited,
        "responded": total_responded,
        "present": total_present,
        "attendance_rate": round((total_present / total_invited) * 100, 2) if total_invited else 0.0
    }


def get_feedback_stats(event):
    """
    Returns feedback statistics (average rating, total comments) for an event.
    """
    feedback_qs = EventFeedback.objects.filter(event=event)
    return {
        "average_rating": round(feedback_qs.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
        "total_feedback": feedback_qs.count(),
        "comments_count": feedback_qs.filter(~Q(comment="")).count()
    }


def get_engagement_over_time(institution, days=30):
    """
    Returns daily counts of created events, RSVPs, and feedbacks over the last 'days' days.
    """
    base = timezone.now().date()
    start = base - timedelta(days=days)

    events = (
        Event.objects.filter(institution=institution, created_at__date__gte=start)
        .extra({'day': "date(created_at)"})
        .values('day')
        .annotate(event_count=Count('id'))
    )

    rsvps = (
        EventRSVP.objects.filter(event__institution=institution, responded_at__date__gte=start)
        .extra({'day': "date(responded_at)"})
        .values('day')
        .annotate(rsvp_count=Count('id'))
    )

    feedbacks = (
        EventFeedback.objects.filter(event__institution=institution, submitted_at__date__gte=start)
        .extra({'day': "date(submitted_at)"})
        .values('day')
        .annotate(feedback_count=Count('id'))
    )

    return {
        "events": list(events),
        "rsvps": list(rsvps),
        "feedbacks": list(feedbacks),
    }
