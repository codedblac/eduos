import django_filters
from .models import (
    AlumniProfile, AlumniEvent, AlumniDonation,
    AlumniMentorship, AlumniAchievement, AlumniNotification,
    AlumniFeedback, AlumniMembership, AlumniVolunteer
)


class AlumniProfileFilter(django_filters.FilterSet):
    graduation_year = django_filters.NumberFilter(field_name='graduation_year')
    course = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = AlumniProfile
        fields = ['graduation_year', 'course', 'gender']


class AlumniEventFilter(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = AlumniEvent
        fields = ['type', 'date']


class AlumniDonationFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(field_name='donated_on')

    class Meta:
        model = AlumniDonation
        fields = ['amount', 'donated_on']


class AlumniMentorshipFilter(django_filters.FilterSet):
    status = django_filters.CharFilter()

    class Meta:
        model = AlumniMentorship
        fields = ['status']


class AlumniAchievementFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = AlumniAchievement
        fields = ['category']


class AlumniNotificationFilter(django_filters.FilterSet):
    type = django_filters.CharFilter()
    sent_on = django_filters.DateFromToRangeFilter()

    class Meta:
        model = AlumniNotification
        fields = ['type', 'sent_on']


class AlumniFeedbackFilter(django_filters.FilterSet):
    rating = django_filters.RangeFilter()

    class Meta:
        model = AlumniFeedback
        fields = ['rating']


class AlumniMembershipFilter(django_filters.FilterSet):
    active = django_filters.BooleanFilter()

    class Meta:
        model = AlumniMembership
        fields = ['active']


class AlumniVolunteerFilter(django_filters.FilterSet):
    status = django_filters.CharFilter()

    class Meta:
        model = AlumniVolunteer
        fields = ['status']
