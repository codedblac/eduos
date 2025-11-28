import django_filters
from .models import AcademicYear, Term, AcademicEvent, HolidayBreak


class AcademicYearFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    is_current = django_filters.BooleanFilter()
    start_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = AcademicYear
        fields = [ 'is_current', 'start_date', 'end_date']


class TermFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    academic_year = django_filters.CharFilter(field_name='academic_year__name', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    start_date = django_filters.DateFromToRangeFilter()
    midterm_date = django_filters.DateFromToRangeFilter()
    end_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Term
        fields = [ 'academic_year', 'is_active', 'start_date', 'midterm_date', 'end_date']


class AcademicEventFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    is_school_wide = django_filters.BooleanFilter()
    start_date = django_filters.DateFromToRangeFilter()
    end_date = django_filters.DateFromToRangeFilter()
    academic_year = django_filters.CharFilter(field_name='academic_year__name', lookup_expr='icontains')
    term = django_filters.CharFilter(field_name='term__name', lookup_expr='icontains')

    class Meta:
        model = AcademicEvent
        fields = ['title', 'is_school_wide', 'start_date', 'end_date', 'academic_year', 'term']


class HolidayBreakFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    start_date = django_filters.DateFromToRangeFilter()
    end_date = django_filters.DateFromToRangeFilter()
    term = django_filters.CharFilter(field_name='term__name', lookup_expr='icontains')

    class Meta:
        model = HolidayBreak
        fields = ['title', 'start_date', 'end_date', 'term']
