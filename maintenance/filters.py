import django_filters
from .models import (
    MaintenanceRequest,
    Equipment,
    MaintenanceSchedule,
    MaintenanceLog
)

class EquipmentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    type = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter()
    institution = django_filters.NumberFilter()

    class Meta:
        model = Equipment
        fields = ['name', 'type', 'status', 'institution']


class MaintenanceRequestFilter(django_filters.FilterSet):
    status = django_filters.CharFilter()
    priority = django_filters.CharFilter()
    equipment__name = django_filters.CharFilter(lookup_expr='icontains')
    reported_by = django_filters.NumberFilter(field_name='reported_by__id')
    institution = django_filters.NumberFilter()

    class Meta:
        model = MaintenanceRequest
        fields = ['status', 'priority', 'equipment__name', 'reported_by', 'institution']


class MaintenanceScheduleFilter(django_filters.FilterSet):
    equipment__name = django_filters.CharFilter(lookup_expr='icontains')
    frequency = django_filters.CharFilter()
    next_maintenance_date = django_filters.DateFromToRangeFilter()
    institution = django_filters.NumberFilter()

    class Meta:
        model = MaintenanceSchedule
        fields = ['equipment__name', 'frequency', 'next_maintenance_date', 'institution']


class MaintenanceLogFilter(django_filters.FilterSet):
    equipment__name = django_filters.CharFilter(lookup_expr='icontains')
    performed_by = django_filters.NumberFilter(field_name='performed_by__id')
    performed_on = django_filters.DateFromToRangeFilter()
    institution = django_filters.NumberFilter()

    class Meta:
        model = MaintenanceLog
        fields = ['equipment__name', 'performed_by', 'performed_on', 'institution']
