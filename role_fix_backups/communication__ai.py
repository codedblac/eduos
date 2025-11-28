from datetime import timedelta
from django.db import models

from django.utils import timezone
from django.db.models import Count, Q, Avg
from .models import CommunicationAnnouncement, CommunicationReadLog, CommunicationTarget
from accounts.models import CustomUser
from institutions.models import Institution
import random

class CommunicationAI:
    """
    AI Engine for analyzing communication behavior and optimizing announcement strategies.
    """

    @staticmethod
    def predict_optimal_delivery_time(user):
        """
        Suggest optimal time to send announcements based on user's past read patterns.
        """
        logs = CommunicationReadLog.objects.filter(user=user)
        if not logs.exists():
            return timezone.now().replace(hour=9, minute=0)  # default morning

        hour_counts = logs.annotate(hour=models.functions.ExtractHour('read_at'))\
                          .values('hour')\
                          .annotate(total=Count('id'))\
                          .order_by('-total')

        best_hour = hour_counts[0]['hour'] if hour_counts else 9
        return timezone.now().replace(hour=best_hour, minute=0)

    @staticmethod
    def recommend_announcement_targets(institution):
        """
        Recommend roles, classes, or streams that frequently interact with communications.
        """
        target_counts = CommunicationTarget.objects.filter(
            announcement__institution=institution
        ).values('primary_role').annotate(total=Count('id')).order_by('-total')

        top_roles = [target['primary_role'] for target in target_counts[:3]]
        return top_roles

    @staticmethod
    def detect_low_engagement_announcements():
        """
        Identify announcements that received poor visibility or no interactions.
        """
        cutoff = timezone.now() - timedelta(days=7)
        announcements = CommunicationAnnouncement.objects.filter(created_at__lte=cutoff, is_archived=False)
        low_engagement = []

        for ann in announcements:
            if ann.read_logs.count() < 3 and not ann.sent:
                low_engagement.append(ann)

        return low_engagement

    @staticmethod
    def auto_tag_announcement(title, content):
        """
        Auto-suggest tags based on title and content.
        Placeholder for future NLP integration.
        """
        keywords = []
        text = f"{title.lower()} {content.lower()}"
        for word in ["exam", "fee", "event", "holiday", "meeting", "sports"]:
            if word in text:
                keywords.append(word)
        return ", ".join(keywords)

    @staticmethod
    def prioritize_announcements():
        """
        Automatically set priority based on content length, keywords, and scheduled time.
        """
        updates = []
        announcements = CommunicationAnnouncement.objects.filter(priority='normal', is_archived=False)

        for ann in announcements:
            if any(word in ann.title.lower() for word in ["urgent", "deadline", "immediate"]):
                ann.priority = 'urgent'
            elif len(ann.content) > 500:
                ann.priority = 'high'
            elif ann.scheduled_at and ann.scheduled_at <= timezone.now() + timedelta(hours=1):
                ann.priority = 'high'
            ann.save()
            updates.append(ann)

        return updates
