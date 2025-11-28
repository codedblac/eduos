from institutions.models import Institution
from collections import Counter
from django.db.models import Count
import random


class InstitutionAIEngine:
    """
    AI Engine for institution-level insights, tagging, recommendations,
    auto-classification, and location/funding analytics.
    """

    def __init__(self, queryset=None):
        # Allows filtering by institution admin or superadmin view
        self.queryset = queryset or Institution.objects.all()

    def top_counties_by_school_count(self, top_n=10):
        """
        Return top N counties with the highest number of registered institutions.
        """
        data = (
            self.queryset
            .values('county')
            .annotate(count=Count('id'))
            .order_by('-count')[:top_n]
        )
        return [{"county": item['county'], "count": item['count']} for item in data]

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
        Returns the most common funding sources.
        """
        sources = self.queryset.exclude(funding_source__isnull=True).values_list('funding_source', flat=True)
        return [{"funding_source": src, "count": cnt} for src, cnt in Counter(sources).most_common(top_n)]

    def get_location_breakdown(self, country=None):
        """
        Returns a nested dict: county -> number of institutions, optionally filtered by country.
        """
        qs = self.queryset
        if country:
            qs = qs.filter(country__iexact=country)
        data = qs.values('county').annotate(count=Count('id')).order_by('-count')
        return {item['county']: item['count'] for item in data}

    def ai_dashboard_summary(self, top_counties=5, top_funding_sources=5):
        """
        Returns a summary suitable for AI-powered dashboards:
        - top counties
        - common funding sources
        """
        return {
            "top_counties": self.top_counties_by_school_count(top_n=top_counties),
            "common_funding_sources": self.common_funding_sources(top_n=top_funding_sources)
        }

    def random_recommendations(self, school_name=None):
        """
        Returns a quick recommendation set for theming and classification.
        """
        school_type = self.suggest_school_type(school_name or "")
        return {
            "suggested_school_type": school_type,
            "theme_color": self.recommend_theme_color(school_type),
            "suggested_secondary_colors": [self.recommend_theme_color(random.choice(list(Institution.InstitutionType.values))) for _ in range(3)]
        }
