# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Item, StockAlert
from datetime import timedelta

@shared_task
def check_low_stock_items():
    """
    Runs daily to evaluate if any items are below their min stock level and create/update alerts.
    """
    items = Item.objects.all()
    for item in items:
        current_stock = item.current_stock()
        if current_stock <= item.min_stock_level:
            alert, created = StockAlert.objects.get_or_create(
                item=item,
                institution=item.institution,
                defaults={"alert_triggered": True}
            )
            if not created and not alert.alert_triggered:
                alert.alert_triggered = True
                alert.save()
        else:
            StockAlert.objects.filter(item=item, alert_triggered=True).update(alert_triggered=False)

@shared_task
def weekly_inventory_summary():
    """
    Sends a weekly inventory summary (future: via email or dashboard)
    """
    # Placeholder for future implementation with report sending
    return "Inventory summary task ran successfully."
