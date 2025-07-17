# alumni/filters.py

import django_filters
from .models import (
    AlumniProfile, AlumniEvent, AlumniDonation,
    AlumniMentorship, AlumniAchievement, AlumniEmployment
)
from institutions.models import Institution
from students.models import Student


class AlumniProfileFilter(django_filters.FilterSet):
    profession = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    university = django_filters.CharFilter(lookup_expr='icontains')
    course = django_filters.CharFilter(lookup_expr='icontains')
    is_verified = django_filters.BooleanFilter()
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = AlumniProfile
        fields = ['profession', 'country', 'university', 'course', 'is_verified', 'institution']


class AlumniEventFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    event_date = django_filters.DateFromToRangeFilter()
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = AlumniEvent
        fields = ['title', 'event_date', 'institution']


class AlumniDonationFilter(django_filters.FilterSet):
    alumni__student__full_name = django_filters.CharFilter(lookup_expr='icontains', label="Alumni Name")
    amount = django_filters.RangeFilter()
    donated_on = django_filters.DateFromToRangeFilter()
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = AlumniDonation
        fields = ['alumni', 'amount', 'donated_on', 'institution']


class AlumniMentorshipFilter(django_filters.FilterSet):
    mentor__profession = django_filters.CharFilter(lookup_expr='icontains')
    mentee__user__full_name = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=[('active', 'Active'), ('ended', 'Ended')])
    start_date = django_filters.DateFromToRangeFilter()
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = AlumniMentorship
        fields = ['mentor', 'mentee', 'status', 'start_date', 'institution']


class AlumniAchievementFilter(django_filters.FilterSet):
    alumni__student__full_name = django_filters.CharFilter(lookup_expr='icontains')
    title = django_filters.CharFilter(lookup_expr='icontains')
    date_achieved = django_filters.DateFromToRangeFilter()
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = AlumniAchievement
        fields = ['alumni', 'title', 'date_achieved', 'institution']


class AlumniEmploymentFilter(django_filters.FilterSet):
    alumni__student__full_name = django_filters.CharFilter(lookup_expr='icontains')
    company_name = django_filters.CharFilter(lookup_expr='icontains')
    currently_employed = django_filters.BooleanFilter()
    start_date = django_filters.DateFromToRangeFilter()
    end_date = django_filters.DateFromToRangeFilter()
    industry = django_filters.CharFilter(lookup_expr='icontains')
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = AlumniEmployment
        fields = [
            'alumni', 'company_name', 'currently_employed',
            'start_date', 'end_date', 'industry', 'institution'
        ]
