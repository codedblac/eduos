from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q, F, Prefetch
from .models import ELibraryResource, ResourceViewLog, ELibraryTag, ELibraryCategory
from accounts.models import CustomUser as User
from institutions.models import Institution
import random


class ELibraryAIEngine:
    """
    AI Engine for the e_library app: provides insights, content tagging,
    recommendations, and analytics.
    """

    @staticmethod
    def analyze_resource_popularity(institution_id=None, days=30):
        """
        Get the top viewed resources over the last `days` (default 30).
        Returns id, title, usage count.
        """
        since = timezone.now() - timedelta(days=days)

        logs_qs = ResourceViewLog.objects.filter(viewed_at__gte=since)

        if institution_id:
            logs_qs = logs_qs.filter(resource__institution_id=institution_id)

        resource_stats = (
            logs_qs.values('resource__id', 'resource__title')
            .annotate(usage_count=Count('id'))
            .order_by('-usage_count')[:10]
        )

        return [
            {
                'id': item['resource__id'],
                'title': item['resource__title'],
                'usage_count': item['usage_count']
            }
            for item in resource_stats
        ]

    @staticmethod
    def recommend_resources_for_user(user: User, count=5):
        """
        Recommends `count` resources based on:
        - Institutional relevance
        - Public trending resources
        - Tag match (if future AI tagging enabled)
        """
        institution_id = getattr(user, 'institution_id', None)
        recommendations = []

        if institution_id:
            institutional_qs = ELibraryResource.objects.filter(
                institution_id=institution_id,
                visibility__in=['institution', 'all'],
                is_approved=True
            ).order_by('-created_at')[:count]
            recommendations.extend(list(institutional_qs))

        if len(recommendations) < count:
            needed = count - len(recommendations)
            public_qs = ELibraryResource.objects.filter(
                visibility='public',
                is_approved=True
            ).order_by('-created_at')[:needed]
            recommendations.extend(list(public_qs))

        return [
            {
                'id': str(res.id),
                'title': res.title,
                'description': res.description[:100] + '...' if res.description else '',
                'resource_type': res.resource_type,
                'visibility': res.visibility,
            } for res in recommendations
        ]

    @staticmethod
    def generate_content_summary(resource: ELibraryResource) -> str:
        """
        Placeholder for LLM-based summarization.
        Currently uses first 150 chars of description.
        """
        content = resource.description or ''
        return content[:150] + ('...' if len(content) > 150 else '')

    @staticmethod
    def detect_content_topics(resource: ELibraryResource) -> list:
        """
        Rudimentary keyword extraction from description.
        Upgradeable to spaCy/NLP/embedding-based classification.
        """
        text = resource.description or ''
        common_words = {
            'the', 'and', 'is', 'in', 'of', 'to', 'a', 'for', 'on',
            'with', 'as', 'by', 'at', 'an', 'be', 'this', 'that',
            'which', 'are', 'was', 'were', 'from', 'it', 'its', 'or'
        }

        words = [word.strip('.,!?()"') for word in text.lower().split()]
        keywords = [word for word in words if word.isalpha() and word not in common_words and len(word) > 3]

        top_keywords = list(dict.fromkeys(keywords))[:5]  # Remove duplicates and limit
        return top_keywords

    @staticmethod
    def analyze_usage_trends(days=30):
        """
        Basic time-windowed trend analysis.
        """
        since = timezone.now() - timedelta(days=days)

        usage = ResourceViewLog.objects.filter(viewed_at__gte=since)
        trending_types = (
            usage.values('resource__resource_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        top_type = trending_types[0]['resource__resource_type'] if trending_types else None

        return {
            'most_viewed_type': top_type,
            'total_views': usage.count(),
            'summary': f"Trending resource type: {top_type}" if top_type else "No data"
        }

    @staticmethod
    def auto_approve_eligible_resources():
        """
        Automatically approves public resources with 10+ views and no reported issues.
        Placeholder logic — requires issue flagging to be implemented.
        """
        eligible = ELibraryResource.objects.annotate(
            views=Count('views')
        ).filter(
            views__gte=10,
            is_approved=False,
            visibility='public'
        )
        count = eligible.update(is_approved=True)
        return count
