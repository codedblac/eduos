# analytics.py
from .models import Item, ItemStockEntry, ItemIssue, ItemReturn, ItemDamage
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta


def get_stock_summary(institution):
    """
    Total stock value and quantity per item
    """
    summary = []
    for item in Item.objects.filter(institution=institution):
        current = item.current_stock()
        summary.append({
            'item': item.name,
            'category': item.category.name if item.category else None,
            'unit': item.unit.name if item.unit else None,
            'current_stock': current,
            'min_stock': item.min_stock_level,
            'stock_status': 'Low' if current <= item.min_stock_level else 'Normal'
        })
    return summary


def usage_report(institution, days=30):
    """
    Returns most used items in last N days
    """
    recent = timezone.now() - timedelta(days=days)
    return ItemIssue.objects.filter(
        institution=institution,
        date_issued__gte=recent
    ).values('item__name').annotate(
        total_issued=Sum('quantity')
    ).order_by('-total_issued')


def damage_report(institution, days=60):
    """
    Items frequently damaged recently
    """
    recent = timezone.now() - timedelta(days=days)
    return ItemDamage.objects.filter(
        institution=institution,
        date_reported__gte=recent
    ).values('item__name').annotate(
        damage_count=Count('id')
    ).order_by('-damage_count')


def return_rate(institution, days=60):
    """
    Return ratio per item for auditing
    """
    recent = timezone.now() - timedelta(days=days)
    returns = ItemReturn.objects.filter(
        institution=institution,
        date_returned__gte=recent
    ).values('item__name').annotate(
        total_returned=Sum('quantity')
    )
    return list(returns)
