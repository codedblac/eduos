from institutions.models import Institution
from django.db.models import Count, Q
from datetime import datetime
from collections import defaultdict


class InstitutionAnalytics:
    """
    Analytics engine for institution-level trends, dashboards, and performance insights.
    """

    def __init__(self, queryset=None):
        self.queryset = queryset or Institution.objects.all()

    def total_institutions(self):
        """
        Return total number of registered institutions.
        """
        return self.queryset.count()

    def institutions_by_type(self):
        """
        Return count of institutions per school_type.
        """
        return self.queryset.values('school_type').annotate(count=Count('id')).order_by('-count')

    def institutions_by_county(self, country=None):
        """
        Return number of institutions per county (optionally filtered by country).
        """
        qs = self.queryset
        if country:
            qs = qs.filter(country__iexact=country)
        return qs.values('county').annotate(count=Count('id')).order_by('-count')

    def growth_by_year(self):
        """
        Returns year-wise institution registration growth (based on established_year).
        """
        return (
            self.queryset.exclude(established_year__isnull=True)
            .values('established_year')
            .annotate(count=Count('id'))
            .order_by('established_year')
        )

    def recent_institutions(self, limit=10):
        """
        Return recently added institutions.
        """
        return self.queryset.order_by('-created_at')[:limit]

    def get_location_matrix(self):
        """
        Return nested breakdown by county → sub_county → ward.
        """
        matrix = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        for institution in self.queryset:
            county = institution.county or "Unknown"
            sub_county = institution.sub_county or "Unknown"
            ward = institution.ward or "Unknown"
            matrix[county][sub_county][ward] += 1

        return matrix
