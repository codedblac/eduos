import django_filters
from .models import (
    VisitorLog, Appointment, ParcelDelivery, GatePass,
    FrontDeskTicket, FrontAnnouncement, SecurityLog
)


class VisitorLogFilter(django_filters.FilterSet):
    visit_date = django_filters.DateFromToRangeFilter()
    visit_purpose = django_filters.CharFilter(lookup_expr='icontains')
    visitor_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = VisitorLog
        fields = ['visit_date', 'visit_purpose', 'visitor_name', 'institution']


class AppointmentFilter(django_filters.FilterSet):
    meeting_date = django_filters.DateFromToRangeFilter()
    visitor_name = django_filters.CharFilter(lookup_expr='icontains')
    meeting_with__email = django_filters.CharFilter(field_name='meeting_with__email', lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Appointment.STATUS_CHOICES)

    class Meta:
        model = Appointment
        fields = ['meeting_date', 'visitor_name', 'meeting_with__email', 'status']


class ParcelDeliveryFilter(django_filters.FilterSet):
    delivered_on = django_filters.DateFromToRangeFilter()
    recipient_type = django_filters.CharFilter(lookup_expr='icontains')
    sender_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ParcelDelivery
        fields = ['recipient_type', 'status', 'delivered_on', 'sender_name']


class GatePassFilter(django_filters.FilterSet):
    exit_time = django_filters.DateFromToRangeFilter()
    reason = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = GatePass
        fields = ['status', 'approved_by', 'exit_time', 'reason']


class FrontDeskTicketFilter(django_filters.FilterSet):
    submitted_on = django_filters.DateFromToRangeFilter()
    category = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=FrontDeskTicket.STATUS_CHOICES)

    class Meta:
        model = FrontDeskTicket
        fields = ['status', 'category', 'submitted_on']


class FrontAnnouncementFilter(django_filters.FilterSet):
    created_on = django_filters.DateFromToRangeFilter()

    class Meta:
        model = FrontAnnouncement
        fields = ['institution', 'created_on']


class SecurityLogFilter(django_filters.FilterSet):
    timestamp = django_filters.DateFromToRangeFilter()
    entry_type = django_filters.ChoiceFilter(choices=SecurityLog.ENTRY_TYPE_CHOICES)

    class Meta:
        model = SecurityLog
        fields = ['entry_type', 'recorded_by', 'timestamp', 'person_name']
