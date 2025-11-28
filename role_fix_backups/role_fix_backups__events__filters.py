import django_filters
from django import forms
from .models import (
    Event, EventRSVP, EventAttendance, EventFeedback,
    EventType, RecurringEventRule
)


class EventFilter(django_filters.FilterSet):
    event_type = django_filters.ChoiceFilter(choices=EventType.choices)
    is_virtual = django_filters.BooleanFilter()
    is_recurring = django_filters.BooleanFilter()
    requires_rsvp = django_filters.BooleanFilter()
    allow_feedback = django_filters.BooleanFilter()
    allow_comments = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()

    start_time = django_filters.DateTimeFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'datetime-local'})
    )
    end_time = django_filters.DateTimeFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'datetime-local'})
    )
    created_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'})
    )

    class Meta:
        model = Event
        fields = [
            'event_type', 'is_virtual', 'is_recurring', 'requires_rsvp',
            'allow_feedback', 'allow_comments', 'is_active',
            'start_time', 'end_time', 'created_at', 'institution',
        ]


class EventRSVPFilter(django_filters.FilterSet):
    response = django_filters.ChoiceFilter(choices=[('yes', 'Yes'), ('no', 'No'), ('maybe', 'Maybe')])
    responded_at = django_filters.DateTimeFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = EventRSVP
        fields = ['event', 'user', 'response', 'responded_at']


class EventAttendanceFilter(django_filters.FilterSet):
    is_present = django_filters.BooleanFilter()
    timestamp = django_filters.DateTimeFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = EventAttendance
        fields = ['event', 'user', 'is_present', 'timestamp']


class EventFeedbackFilter(django_filters.FilterSet):
    rating = django_filters.RangeFilter()
    submitted_at = django_filters.DateTimeFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = EventFeedback
        fields = ['event', 'user', 'rating', 'submitted_at']


class RecurringEventRuleFilter(django_filters.FilterSet):
    frequency = django_filters.ChoiceFilter(choices=RecurringEventRule.FREQUENCY_CHOICES)
    interval = django_filters.RangeFilter()
    end_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = RecurringEventRule
        fields = ['frequency', 'interval', 'end_date']
