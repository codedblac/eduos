import django_filters
from django.db.models import Q
from .models import (
    TransportRoute, Vehicle, Driver, TransportAssignment,
    TransportAttendance, VehicleLog, TripLog,
    TransportNotification, TransportBooking, MaintenanceRecord
)


class TransportRouteFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter()
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = TransportRoute
        fields = ['is_active', 'institution']


class VehicleFilter(django_filters.FilterSet):
    assigned_route = django_filters.NumberFilter(field_name='assigned_route_id')
    insurance_expiry = django_filters.DateFromToRangeFilter()
    last_service_date = django_filters.DateFromToRangeFilter()
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = Vehicle
        fields = ['assigned_route', 'insurance_expiry', 'last_service_date', 'institution']


class DriverFilter(django_filters.FilterSet):
    assigned_vehicle = django_filters.NumberFilter(field_name='assigned_vehicle_id')
    license_expiry = django_filters.DateFromToRangeFilter()
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = Driver
        fields = ['assigned_vehicle', 'license_expiry', 'institution']


class TransportAssignmentFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    route = django_filters.NumberFilter(field_name='route_id')
    is_active = django_filters.BooleanFilter()
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = TransportAssignment
        fields = ['student', 'route', 'is_active', 'institution']


class TransportAttendanceFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    date = django_filters.DateFromToRangeFilter()
    status = django_filters.CharFilter(lookup_expr='iexact')
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = TransportAttendance
        fields = ['student', 'date', 'status', 'institution']


class VehicleLogFilter(django_filters.FilterSet):
    vehicle = django_filters.NumberFilter(field_name='vehicle_id')
    date = django_filters.DateFromToRangeFilter()
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = VehicleLog
        fields = ['vehicle', 'date', 'institution']


class TripLogFilter(django_filters.FilterSet):
    vehicle = django_filters.NumberFilter(field_name='vehicle_id')
    driver = django_filters.NumberFilter(field_name='driver_id')
    route = django_filters.NumberFilter(field_name='route_id')
    status = django_filters.CharFilter(lookup_expr='iexact')
    start_time = django_filters.DateTimeFromToRangeFilter()
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = TripLog
        fields = ['vehicle', 'driver', 'route', 'status', 'start_time', 'institution']


class TransportNotificationFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    recipient_guardian = django_filters.NumberFilter(field_name='recipient_guardian_id')
    type = django_filters.CharFilter(lookup_expr='iexact')
    sent_at = django_filters.DateTimeFromToRangeFilter()
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = TransportNotification
        fields = ['student', 'recipient_guardian', 'type', 'sent_at', 'institution']


class TransportBookingFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    vehicle = django_filters.NumberFilter(field_name='vehicle_id')
    route = django_filters.NumberFilter(field_name='route_id')
    status = django_filters.CharFilter(lookup_expr='iexact')
    travel_date = django_filters.DateFromToRangeFilter()
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = TransportBooking
        fields = ['student', 'vehicle', 'route', 'status', 'travel_date', 'institution']


class MaintenanceRecordFilter(django_filters.FilterSet):
    vehicle = django_filters.NumberFilter(field_name='vehicle_id')
    maintenance_type = django_filters.CharFilter(lookup_expr='icontains')
    performed_on = django_filters.DateFromToRangeFilter()
    next_due_date = django_filters.DateFromToRangeFilter()
    institution = django_filters.NumberFilter(field_name="institution_id")

    class Meta:
        model = MaintenanceRecord
        fields = ['vehicle', 'maintenance_type', 'performed_on', 'next_due_date', 'institution']
