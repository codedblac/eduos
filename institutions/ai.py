from institutions.models import Institution
from collections import Counter
from django.db.models import Count
import random


class InstitutionAIEngine:
    """
    AI Engine for institution-level insights, tagging, recommendations, and auto-classification.
    """

    def __init__(self, queryset=None):
        self.queryset = queryset or Institution.objects.all()

    def top_counties_by_school_count(self, top_n=10):
        """
        Return top N counties with the highest number of registered institutions.
        """
        return self.queryset.values('county').annotate(count=Count('id')).order_by('-count')[:top_n]

    def suggest_school_type(self, name):
        """
        Suggest school type based on keywords in name.
        """
        name_lower = name.lower()
        if 'primary' in name_lower:
            return Institution.InstitutionType.PRIMARY
        elif 'secondary' in name_lower:
            return Institution.InstitutionType.SECONDARY
        elif 'university' in name_lower:
            return Institution.InstitutionType.UNIVERSITY
        elif 'technical' in name_lower or 'polytechnic' in name_lower:
            return Institution.InstitutionType.TECHNICAL
        elif 'virtual' in name_lower or 'online' in name_lower:
            return Institution.InstitutionType.VIRTUAL
        return Institution.InstitutionType.OTHER

    def recommend_theme_color(self, school_type):
        """
        Suggest branding color based on school type.
        """
        suggestions = {
            Institution.InstitutionType.PRIMARY: "#2E86C1",
            Institution.InstitutionType.SECONDARY: "#1F618D",
            Institution.InstitutionType.UNIVERSITY: "#154360",
            Institution.InstitutionType.TECHNICAL: "#117864",
            Institution.InstitutionType.VIRTUAL: "#6C3483",
            Institution.InstitutionType.OTHER: "#7D3C98",
        }
        return suggestions.get(school_type, "#0047AB")

    def common_funding_sources(self, top_n=5):
        """
        Returns most common funding sources.
        """
        sources = self.queryset.exclude(funding_source__isnull=True).values_list('funding_source', flat=True)
        return Counter(sources).most_common(top_n)

    def get_location_breakdown(self, country=None):
        """
        Return breakdown of institutions per county, optionally filtered by country.
        """
        qs = self.queryset
        if country:
            qs = qs.filter(country__iexact=country)
        return qs.values('county').annotate(count=Count('id')).order_by('-count')
