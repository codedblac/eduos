from institutions.models import Institution
from django.db.models import Count, Q
from datetime import datetime
from collections import defaultdict


class InstitutionAnalytics:
    """
    Analytics engine for institution-level trends, dashboards, and performance insights.
    Supports optional queryset filtering for multi-tenancy.
    """

    def __init__(self, queryset=None):
        # Allow passing a filtered queryset (e.g., for a single institution or institution admin)
        self.queryset = queryset or Institution.objects.all()

    def total_institutions(self):
        """
        Return total number of institutions in the queryset.
        """
        return self.queryset.count()

    def institutions_by_type(self):
        """
        Returns a dict of institution_type -> count.
        """
        data = (
            self.queryset
            .values('institution_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return {item['institution_type']: item['count'] for item in data}

    def institutions_by_school_type(self):
        """
        Returns a dict of school_type -> count.
        """
        data = (
            self.queryset
            .values('school_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return {item['school_type']: item['count'] for item in data}

    def institutions_by_county(self, country=None):
        """
        Returns a dict of county -> count, optionally filtered by country.
        """
        qs = self.queryset
        if country:
            qs = qs.filter(country__iexact=country)
        data = qs.values('county').annotate(count=Count('id')).order_by('-count')
        return {item['county']: item['count'] for item in data}

    def growth_by_year(self):
        """
        Returns year-wise institution registration growth (established_year).
        """
        data = (
            self.queryset.exclude(established_year__isnull=True)
            .values('established_year')
            .annotate(count=Count('id'))
            .order_by('established_year')
        )
        return {item['established_year']: item['count'] for item in data}

    def recent_institutions(self, limit=10):
        """
        Returns the most recently added institutions (created_at).
        """
        return self.queryset.order_by('-created_at')[:limit]

    def get_location_matrix(self):
        """
        Returns a nested breakdown: county -> sub_county -> ward -> count.
        """
        matrix = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for inst in self.queryset:
            county = inst.county or "Unknown"
            sub_county = inst.sub_county or "Unknown"
            ward = inst.ward or "Unknown"
            matrix[county][sub_county][ward] += 1
        return matrix

    def dashboard_summary(self):
        """
        Returns a summary suitable for dashboards:
        - total institutions
        - institutions by type
        - institutions by school_type
        - recent institutions
        """
        return {
            "total_institutions": self.total_institutions(),
            "institutions_by_type": self.institutions_by_type(),
            "institutions_by_school_type": self.institutions_by_school_type(),
            "recent_institutions": [
                {
                    "id": inst.id,
                    "name": inst.name,
                    "code": inst.code,
                    "created_at": inst.created_at
                } for inst in self.recent_institutions()
            ]
        }
