import django_filters
from .models import (
    VisitorLog, Appointment, ParcelDelivery, GatePass,
    FrontDeskTicket, FrontAnnouncement, SecurityLog
)


class VisitorLogFilter(django_filters.FilterSet):
    check_in__date = django_filters.DateFilter(field_name="check_in", lookup_expr="date")
    check_out__isnull = django_filters.BooleanFilter(field_name="check_out", lookup_expr="isnull")

    class Meta:
        model = VisitorLog
        fields = ['name', 'national_id', 'phone', 'purpose', 'person_to_visit', 'institution']


class AppointmentFilter(django_filters.FilterSet):
    scheduled_time__date = django_filters.DateFilter(field_name="scheduled_time", lookup_expr="date")

    class Meta:
        model = Appointment
        fields = ['visitor_name', 'meeting_with', 'status', 'institution']


class ParcelDeliveryFilter(django_filters.FilterSet):
    received_on__date = django_filters.DateFilter(field_name="received_on", lookup_expr="date")
    picked_up_on__date = django_filters.DateFilter(field_name="picked_up_on", lookup_expr="date")

    class Meta:
        model = ParcelDelivery
        fields = [
            'recipient_student', 'recipient_staff', 'status',
            'sender', 'received_by', 'picked_up_by', 'institution'
        ]


class GatePassFilter(django_filters.FilterSet):
    time_out__date = django_filters.DateFilter(field_name="time_out", lookup_expr="date")
    time_in__isnull = django_filters.BooleanFilter(field_name="time_in", lookup_expr="isnull")

    class Meta:
        model = GatePass
        fields = [
            'issued_to_student', 'issued_to_staff', 'reason',
            'approved_by', 'is_returned', 'institution'
        ]


class FrontDeskTicketFilter(django_filters.FilterSet):
    created_on__date = django_filters.DateFilter(field_name="created_on", lookup_expr="date")

    class Meta:
        model = FrontDeskTicket
        fields = ['category', 'status', 'submitted_by', 'institution']


class FrontAnnouncementFilter(django_filters.FilterSet):
    display_from__date = django_filters.DateFilter(field_name="display_from", lookup_expr="date")
    display_until__date = django_filters.DateFilter(field_name="display_until", lookup_expr="date")

    class Meta:
        model = FrontAnnouncement
        fields = ['title', 'created_by', 'institution']


class SecurityLogFilter(django_filters.FilterSet):
    time_in__date = django_filters.DateFilter(field_name="time_in", lookup_expr="date")
    time_out__isnull = django_filters.BooleanFilter(field_name="time_out", lookup_expr="isnull")

    class Meta:
        model = SecurityLog
        fields = ['entry_type', 'name_or_plate', 'recorded_by', 'institution']
