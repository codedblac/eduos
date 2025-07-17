from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    ELibraryResource,
    ResourceViewLog,
    ResourceVersion,
    ELibraryCategory,
    ELibraryTag
)
from institutions.models import Institution
from accounts.models import CustomUser


class ELibraryAnalytics:

    @staticmethod
    def most_viewed_resources(limit=10, days=30, institution_id=None):
        """
        Returns the most viewed resources in the past `days`, optionally filtered by institution.
        """
        since = timezone.now() - timedelta(days=days)
        queryset = ResourceViewLog.objects.filter(viewed_at__gte=since)

        if institution_id:
            queryset = queryset.filter(resource__institution_id=institution_id)

        stats = queryset.values('resource__id', 'resource__title').annotate(
            views=Count('id')
        ).order_by('-views')[:limit]

        return [
            {
                'resource_id': stat['resource__id'],
                'title': stat['resource__title'],
                'view_count': stat['views']
            } for stat in stats
        ]

    @staticmethod
    def active_users(limit=5, days=30):
        """
        Users who viewed the most resources in the given time period.
        """
        since = timezone.now() - timedelta(days=30)
        stats = ResourceViewLog.objects.filter(viewed_at__gte=since).values(
            'user__id', 'user__username'
        ).annotate(
            total_views=Count('id')
        ).order_by('-total_views')[:limit]

        return [
            {
                'user_id': s['user__id'],
                'username': s['user__username'],
                'view_count': s['total_views']
            } for s in stats
        ]

    @staticmethod
    def resource_type_distribution(institution_id=None):
        """
        Returns count of each resource type.
        """
        queryset = ELibraryResource.objects.all()
        if institution_id:
            queryset = queryset.filter(institution_id=institution_id)

        return queryset.values('resource_type').annotate(
            count=Count('id')
        ).order_by('-count')

    @staticmethod
    def resource_visibility_stats(institution_id=None):
        """
        Returns count of resources grouped by visibility.
        """
        queryset = ELibraryResource.objects.all()
        if institution_id:
            queryset = queryset.filter(institution_id=institution_id)

        return queryset.values('visibility').annotate(
            count=Count('id')
        ).order_by('-count')

    @staticmethod
    def growth_over_time(interval='monthly', months=6):
        """
        Track growth in uploaded resources over time.
        `interval` can be 'daily', 'weekly', or 'monthly'.
        """
        now = timezone.now()
        stats = []

        for i in range(months):
            if interval == 'monthly':
                start = now - timedelta(days=30 * (i + 1))
                end = now - timedelta(days=30 * i)
            elif interval == 'weekly':
                start = now - timedelta(weeks=(i + 1))
                end = now - timedelta(weeks=i)
            elif interval == 'daily':
                start = now - timedelta(days=(i + 1))
                end = now - timedelta(days=i)
            else:
                continue

            count = ELibraryResource.objects.filter(
                created_at__gte=start, created_at__lt=end
            ).count()

            stats.append({
                'period_start': start.date(),
                'period_end': end.date(),
                'new_resources': count
            })

        return list(reversed(stats))

    @staticmethod
    def most_used_categories(limit=5):
        """
        Categories with the most resources.
        """
        return ELibraryCategory.objects.annotate(
            resource_count=Count('resources')
        ).order_by('-resource_count')[:limit]

    @staticmethod
    def most_used_tags(limit=10):
        """
        Most frequently used tags.
        """
        return ELibraryTag.objects.annotate(
            usage=Count('resources')
        ).order_by('-usage')[:limit]

    @staticmethod
    def versioned_resources_count():
        """
        Count how many resources have version history.
        """
        return ELibraryResource.objects.annotate(
            version_count=Count('versions')
        ).filter(version_count__gt=0).count()

    @staticmethod
    def recently_added_resources(limit=5):
        """
        Latest uploaded resources.
        """
        return ELibraryResource.objects.select_related('institution').order_by('-created_at')[:limit]
