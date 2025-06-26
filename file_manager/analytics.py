from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import ManagedFile, FileAccessLog, FileVersion


class FileManagerAnalytics:
    """
    Analytical methods for usage insights and reporting in the file manager app.
    """

    @staticmethod
    def most_downloaded_files(limit=10):
        """
        Return top files ordered by download count.
        """
        return ManagedFile.objects.annotate(
            download_count=Count('accesslog', filter=Q(accesslog__action='downloaded'))
        ).order_by('-download_count')[:limit]

    @staticmethod
    def most_viewed_files(limit=10):
        """
        Return top files ordered by view count.
        """
        return ManagedFile.objects.annotate(
            view_count=Count('accesslog', filter=Q(accesslog__action='viewed'))
        ).order_by('-view_count')[:limit]

    @staticmethod
    def activity_by_user(user):
        """
        Return access logs for a specific user.
        """
        return FileAccessLog.objects.filter(user=user).order_by('-accessed_at')

    @staticmethod
    def uploads_per_user(limit=10):
        """
        Return upload counts per user.
        """
        return ManagedFile.objects.values(
            'uploaded_by__id', 'uploaded_by__username'
        ).annotate(
            total_uploads=Count('id')
        ).order_by('-total_uploads')[:limit]

    @staticmethod
    def file_type_distribution():
        """
        Return count of files by type.
        """
        return ManagedFile.objects.values(
            'file_type'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

    @staticmethod
    def recent_uploads(days=7):
        """
        Return files uploaded in the last N days.
        """
        since = timezone.now() - timedelta(days=days)
        return ManagedFile.objects.filter(created_at__gte=since).order_by('-created_at')

    @staticmethod
    def version_history_summary(file_id):
        """
        Return version history of a given file.
        """
        return FileVersion.objects.filter(managed_file_id=file_id).order_by('-version_number')

    @staticmethod
    def access_trend(file: ManagedFile, days=30):
        """
        Return daily view/download stats for a file.
        Useful for plotting trends.
        """
        since = timezone.now() - timedelta(days=days)
        return FileAccessLog.objects.filter(
            file=file,
            accessed_at__gte=since
        ).extra(select={'day': "DATE(accessed_at)"}).values('day', 'action').annotate(
            count=Count('id')
        ).order_by('day')

    @staticmethod
    def stale_files(days=180):
        """
        Return files not accessed in the last N days.
        """
        cutoff = timezone.now() - timedelta(days=days)
        return ManagedFile.objects.exclude(
            accesslog__accessed_at__gte=cutoff
        ).distinct().order_by('updated_at')
