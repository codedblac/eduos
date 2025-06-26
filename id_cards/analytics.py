from django.db.models import Count
from django.utils import timezone
from .models import IDCard


def get_idcard_statistics(institution):
    """
    Return statistics on ID card generation per role within an institution.
    """
    stats = IDCard.objects.filter(institution=institution).values('role').annotate(
        total=Count('id')
    )
    return {entry['role']: entry['total'] for entry in stats}


def get_daily_generation_report(institution, days=30):
    """
    Return a breakdown of how many ID cards were generated each day over the last `days`.
    """
    from django.db.models.functions import TruncDate

    recent_cards = IDCard.objects.filter(
        institution=institution,
        created_at__gte=timezone.now() - timezone.timedelta(days=days)
    ).annotate(date=TruncDate('created_at')).values('date').annotate(
        total=Count('id')
    ).order_by('-date')

    return list(recent_cards)


def get_expired_id_cards(institution):
    """
    Returns a queryset of expired ID cards for an institution.
    """
    return IDCard.objects.filter(
        institution=institution,
        expiry_date__lt=timezone.now()
    )


def get_pending_regeneration(institution):
    """
    Returns IDs marked for regeneration (e.g., due to updates or lost cards).
    """
    return IDCard.objects.filter(
        institution=institution,
        status='pending_regeneration'
    )


def get_idcard_overview(institution):
    """
    Aggregated snapshot of ID card statuses.
    """
    total = IDCard.objects.filter(institution=institution).count()
    expired = get_expired_id_cards(institution).count()
    pending = get_pending_regeneration(institution).count()
    return {
        "total_cards": total,
        "expired_cards": expired,
        "pending_regeneration": pending
    }
