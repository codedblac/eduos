from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import AlumniProfile, AlumniContribution, AlumniEvent


class AlumniAnalytics:

    @staticmethod
    def total_alumni(institution=None):
        qs = AlumniProfile.objects.all()
        if institution:
            qs = qs.filter(institution=institution)
        return qs.count()

    @staticmethod
    def alumni_by_year(institution=None):
        qs = AlumniProfile.objects.all()
        if institution:
            qs = qs.filter(institution=institution)
        return qs.values('graduation_year').annotate(total=Count('id')).order_by('graduation_year')

    @staticmethod
    def contribution_totals(institution=None):
        qs = AlumniContribution.objects.all()
        if institution:
            qs = qs.filter(institution=institution)
        return qs.aggregate(total=Sum('amount'), average=Avg('amount'), count=Count('id'))

    @staticmethod
    def monthly_contribution_trend(institution=None, months=6):
        from django.db.models.functions import TruncMonth
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30 * months)
        qs = AlumniContribution.objects.filter(date_contributed__range=[start_date, end_date])
        if institution:
            qs = qs.filter(institution=institution)
        return qs.annotate(month=TruncMonth('date_contributed')).values('month').annotate(total=Sum('amount')).order_by('month')

    @staticmethod
    def top_contributors(limit=5, institution=None):
        qs = AlumniContribution.objects.all()
        if institution:
            qs = qs.filter(institution=institution)
        return qs.values('alumni__user__first_name', 'alumni__user__last_name').annotate(total=Sum('amount')).order_by('-total')[:limit]

    @staticmethod
    def most_active_years(limit=5, institution=None):
        qs = AlumniProfile.objects.all()
        if institution:
            qs = qs.filter(institution=institution)
        return qs.values('graduation_year').annotate(total=Count('id')).order_by('-total')[:limit]

    @staticmethod
    def event_participation_stats(institution=None):
        qs = AlumniEvent.objects.all()
        if institution:
            qs = qs.filter(institution=institution)
        return qs.annotate(attendees_count=Count('attendees')).values('title', 'event_date', 'attendees_count')

    @staticmethod
    def alumni_engagement_distribution(institution=None):
        buckets = {'low': 0, 'medium': 0, 'high': 0}
        qs = AlumniProfile.objects.all()
        if institution:
            qs = qs.filter(institution=institution)
        for profile in qs:
            score = getattr(profile, 'engagement_score', 0)
            if score >= 0.75:
                buckets['high'] += 1
            elif score >= 0.4:
                buckets['medium'] += 1
            else:
                buckets['low'] += 1
        return buckets
