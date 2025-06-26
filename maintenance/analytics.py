# maintenance/analytics.py

from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import MaintenanceRequest, MaintenanceLog, Equipment, Technician


class MaintenanceAnalyticsEngine:

    @staticmethod
    def requests_summary(institution):
        """
        Count requests by status.
        """
        return MaintenanceRequest.objects.filter(institution=institution).values('status').annotate(total=Count('id'))

    @staticmethod
    def technician_performance(institution):
        """
        Number of tasks completed per technician.
        """
        return MaintenanceLog.objects.filter(institution=institution).values('technician__user__full_name').annotate(
            completed_tasks=Count('id'),
            avg_completion_time=Avg('completed_at')  # Assume completed_at - started_at stored
        ).order_by('-completed_tasks')

    @staticmethod
    def top_equipment_by_requests(institution, days=90):
        """
        Equipment with most maintenance requests in a given period.
        """
        since = timezone.now() - timedelta(days=days)
        return MaintenanceRequest.objects.filter(
            institution=institution, created_at__gte=since
        ).values('equipment__name', 'equipment__category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

    @staticmethod
    def open_requests(institution):
        """
        Return list of currently pending or approved requests.
        """
        return MaintenanceRequest.objects.filter(
            institution=institution, status__in=['pending', 'approved']
        ).select_related('equipment', 'reported_by')

    @staticmethod
    def request_trends(institution):
        """
        Return number of requests per month (last 6 months).
        """
        from django.db.models.functions import TruncMonth
        six_months_ago = timezone.now() - timedelta(days=180)
        return MaintenanceRequest.objects.filter(
            institution=institution, created_at__gte=six_months_ago
        ).annotate(month=TruncMonth('created_at')).values('month').annotate(
            count=Count('id')
        ).order_by('month')

    @staticmethod
    def overdue_requests(institution):
        """
        Identify all requests that are overdue (not completed and older than 14 days).
        """
        overdue_threshold = timezone.now() - timedelta(days=14)
        return MaintenanceRequest.objects.filter(
            institution=institution,
            status__in=['pending', 'approved'],
            created_at__lte=overdue_threshold
        ).select_related('equipment', 'reported_by')
