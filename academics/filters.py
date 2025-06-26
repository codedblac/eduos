import django_filters
from .models import AcademicYear, Term, AcademicEvent, HolidayBreak


class AcademicYearFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    is_current = django_filters.BooleanFilter()

    class Meta:
        model = AcademicYear
        fields = ['name', 'is_current']


class TermFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    academic_year = django_filters.CharFilter(field_name='academic_year__name', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Term
        fields = ['name', 'academic_year', 'is_active']


class AcademicEventFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    start_date = django_filters.DateFromToRangeFilter()
    is_school_wide = django_filters.BooleanFilter()
    academic_year = django_filters.CharFilter(field_name='academic_year__name', lookup_expr='icontains')
    term = django_filters.CharFilter(field_name='term__name', lookup_expr='icontains')

    class Meta:
        model = AcademicEvent
        fields = ['title', 'start_date', 'is_school_wide', 'academic_year', 'term']


class HolidayBreakFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    start_date = django_filters.DateFromToRangeFilter()
    term = django_filters.CharFilter(field_name='term__name', lookup_expr='icontains')

    class Meta:
        model = HolidayBreak
        fields = ['title', 'start_date', 'term']
