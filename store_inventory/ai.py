# ai.py
from .models import Item, ItemIssue, ItemStockEntry
from django.db.models import Sum
from datetime import timedelta, date
from django.utils import timezone

class InventoryAI:
    """
    AI-powered engine for predictive inventory insights and automation.
    """

    @staticmethod
    def predict_item_demand(item, past_days=30):
        """
        Predict future demand based on usage in the past N days
        """
        recent_issues = ItemIssue.objects.filter(
            item=item,
            date_issued__gte=timezone.now() - timedelta(days=past_days)
        ).aggregate(total=Sum('quantity'))['total'] or 0

        avg_daily_usage = recent_issues / past_days
        return round(avg_daily_usage * 7)  # predicted need for next week

    @staticmethod
    def flag_restock_urgency(item):
        """
        Return urgency level based on current stock vs. predicted demand
        """
        predicted = InventoryAI.predict_item_demand(item)
        current = item.current_stock()

        if current <= 0:
            return 'critical'
        elif current < predicted:
            return 'urgent'
        elif current < predicted * 2:
            return 'moderate'
        return 'ok'

    @staticmethod
    def recommended_reorder_quantity(item):
        """
        Suggest reorder quantity based on demand and stock trends
        """
        predicted = InventoryAI.predict_item_demand(item)
        buffer = predicted * 2
        return max(buffer - item.current_stock(), 0)

    @staticmethod
    def top_moving_items(institution, days=30):
        """
        List of most issued items for analytics
        """
        return ItemIssue.objects.filter(
            institution=institution,
            date_issued__gte=timezone.now() - timedelta(days=days)
        ).values('item__name').annotate(total=Sum('quantity')).order_by('-total')[:10]
