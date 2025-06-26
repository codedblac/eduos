# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    ItemIssue, ItemReturn, ItemDamage, ItemStockEntry, StockAlert, Item
)

# Utility to check and trigger alert

def evaluate_stock_alert(item):
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
        # Reset alert if stock is back up
        StockAlert.objects.filter(item=item, alert_triggered=True).update(alert_triggered=False)

# When stock is added
@receiver(post_save, sender=ItemStockEntry)
def update_alert_on_stock_entry(sender, instance, **kwargs):
    evaluate_stock_alert(instance.item)

# When item is issued
@receiver(post_save, sender=ItemIssue)
def update_alert_on_issue(sender, instance, **kwargs):
    evaluate_stock_alert(instance.item)

# When items are returned
@receiver(post_save, sender=ItemReturn)
def update_alert_on_return(sender, instance, **kwargs):
    evaluate_stock_alert(instance.item)

# When damage is reported
@receiver(post_save, sender=ItemDamage)
def update_alert_on_damage(sender, instance, **kwargs):
    evaluate_stock_alert(instance.item)

# Re-evaluate on delete (e.g., reverse action)
@receiver(post_delete, sender=ItemIssue)
@receiver(post_delete, sender=ItemReturn)
@receiver(post_delete, sender=ItemDamage)
@receiver(post_delete, sender=ItemStockEntry)
def reevaluate_on_delete(sender, instance, **kwargs):
    evaluate_stock_alert(instance.item)
