from django.db.models import Count, Q
from django.utils import timezone
from django.db.models.functions import TruncDate
from .models import IDCard


def get_idcard_statistics(institution):
    """
    Returns a breakdown of ID card counts per role within a given institution.
    Example output:
        {
            "STUDENT": 1200,
            "TEACHER": 150,
            "STAFF": 50
        }
    """
    stats = IDCard.objects.filter(institution=institution).values('role').annotate(
        total=Count('id')
    )

    return {entry['role']: entry['total'] for entry in stats}


def get_daily_generation_report(institution, days=30):
    """
    Returns the number of ID cards generated daily over the last `days`.
    Output format:
        [
            {"date": "2025-07-01", "total": 30},
            {"date": "2025-07-02", "total": 25},
            ...
        ]
    """
    date_limit = timezone.now() - timezone.timedelta(days=days)

    daily_data = IDCard.objects.filter(
        institution=institution,
        created_at__gte=date_limit
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Count('id')
    ).order_by('-date')

    return list(daily_data)


def get_expired_id_cards(institution):
    """
    Returns a queryset of expired ID cards.
    """
    today = timezone.now().date()
    return IDCard.objects.filter(institution=institution, expiry_date__lt=today)


def get_pending_regeneration(institution):
    """
    Returns a queryset of ID cards marked for pending regeneration.
    """
    return IDCard.objects.filter(institution=institution, status='pending_regeneration')


def get_cards_issued_this_term(institution, term_start, term_end):
    """
    Returns total ID cards issued within the given term date range.
    """
    return IDCard.objects.filter(
        institution=institution,
        created_at__range=(term_start, term_end)
    ).count()


def get_idcard_overview(institution):
    """
    Returns an aggregated snapshot of ID card status for dashboards.
    Output:
        {
            "total_cards": 1400,
            "expired_cards": 120,
            "pending_regeneration": 15,
            "active_cards": 1300,
            "revoked_cards": 10
        }
    """
    total = IDCard.objects.filter(institution=institution).count()
    expired = get_expired_id_cards(institution).count()
    pending = get_pending_regeneration(institution).count()
    active = IDCard.objects.filter(institution=institution, is_active=True).count()
    revoked = IDCard.objects.filter(institution=institution, revoked=True).count()

    return {
        "total_cards": total,
        "active_cards": active,
        "expired_cards": expired,
        "pending_regeneration": pending,
        "revoked_cards": revoked,
    }


def get_idcard_trends(institution, days=90):
    """
    Returns time-series data for ID card generation trends (weekly granularity).
    Useful for analytics charts.
    Output format:
        [
            {"week": "2025-07-01", "total": 120},
            ...
        ]
    """
    from django.db.models.functions import TruncWeek

    start_date = timezone.now() - timezone.timedelta(days=days)

    return IDCard.objects.filter(
        institution=institution,
        created_at__gte=start_date
    ).annotate(
        week=TruncWeek('created_at')
    ).values('week').annotate(
        total=Count('id')
    ).order_by('week')
