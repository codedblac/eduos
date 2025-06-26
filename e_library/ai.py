# e_library/ai.py

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from .models import ELibraryResource
from accounts.models import CustomUser as User
import random

class ELibraryAIEngine:
    """
    AI Engine for e_library app: analyzes usage, recommends content,
    and extracts metadata for better insights.
    """

    @staticmethod
    def analyze_resource_popularity(institution_id=None, days=30):
        """
        Analyze and return the most popular resources in the last `days` days.
        If institution_id is provided, analyze only that institution's resources.
        Returns a list of resource dicts with id, title, usage_count.
        """
        since = timezone.now() - timedelta(days=days)

        queryset = ELibraryResource.objects.filter(
            created_at__gte=since,
        )

        if institution_id:
            queryset = queryset.filter(institution_id=institution_id, visibility='institution')
        else:
            queryset = queryset.filter(visibility='public')

        # Annotate usage_count, fallback gracefully if usage_logs relation doesn't exist
        try:
            queryset = queryset.annotate(usage_count=Count('usage_logs')).order_by('-usage_count', '-created_at')
        except Exception:
            queryset = queryset.order_by('-created_at')

        popular_resources = queryset[:10]

        result = []
        for res in popular_resources:
            result.append({
                'id': str(res.id),
                'title': res.title,
                'usage_count': getattr(res, 'usage_count', 0),
            })
        return result

    @staticmethod
    def recommend_resources_for_user(user: User, count=5):
        """
        Recommend resources for a given user based on:
        - Their institution's popular resources (visibility='institution')
        - Random selection from public resources (visibility='public')
        Returns list of dicts with minimal info.
        """
        institution_id = getattr(user, 'institution_id', None)
        recommendations = []

        if institution_id:
            institution_resources = ELibraryResource.objects.filter(
                institution_id=institution_id,
                visibility='institution',
            ).order_by('-created_at')[:count]
            recommendations.extend(institution_resources)

        if len(recommendations) < count:
            needed = count - len(recommendations)
            public_resources = ELibraryResource.objects.filter(
                visibility='public',
            ).order_by('-created_at')[:needed]
            recommendations.extend(public_resources)

        # Convert queryset or list to dict with minimal fields
        return [{
            'id': str(res.id),
            'title': res.title,
            'description': res.description or "",
            'resource_type': getattr(res, 'resource_type', ''),
        } for res in recommendations]

    @staticmethod
    def generate_content_summary(resource: ELibraryResource):
        """
        Generate a summary of the content (e.g., from text documents or video transcripts).
        Placeholder for integration with an actual NLP model or API.
        """
        text = resource.description or ''
        summary = text[:150] + ('...' if len(text) > 150 else '')
        return summary

    @staticmethod
    def detect_content_topics(resource: ELibraryResource):
        """
        Detect key topics or tags from the resource.
        Placeholder for topic modeling or keyword extraction.
        """
        text = resource.description or ''
        keywords = set()
        words = text.lower().split()
        common_words = {'the', 'and', 'is', 'in', 'of', 'to', 'a', 'for', 'on', 'with', 'as', 'by', 'at', 'an', 'be', 'this', 'that', 'which'}
        for word in words:
            # Only alphabetic words longer than 3 chars and not common words
            if word not in common_words and len(word) > 3 and word.isalpha():
                keywords.add(word)
                if len(keywords) >= 5:
                    break
        return list(keywords)

    @staticmethod
    def analyze_usage_trends():
        """
        Analyze trends over time for resource usage.
        Could be enhanced to provide graphs or alerts.
        """
        # Stub - requires integration with usage logs or analytics data
        return {
            'most_viewed_resource': None,
            'most_active_institution': None,
            'trending_resource_types': [],
            'summary': 'Analytics data not yet implemented.'
        }
