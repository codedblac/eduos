from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    TransportRoute, Vehicle, MaintenanceRecord, Driver,
    TransportBooking, TransportAssignment, TransportAttendance,
    VehicleLog, TripLog, TransportNotification
)


class BaseInstitutionAdmin(admin.ModelAdmin):
    """Filters querysets to only show data belonging to the user's institution."""
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(institution=request.user.institution)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.institution = request.user.institution
        obj.save()


@admin.register(TransportRoute)
class TransportRouteAdmin(BaseInstitutionAdmin):
    list_display = ['name', 'start_location', 'end_location', 'morning_time', 'evening_time', 'is_active']
    search_fields = ['name', 'start_location', 'end_location']
    list_filter = ['institution', 'is_active']


@admin.register(Vehicle)
class VehicleAdmin(BaseInstitutionAdmin):
    list_display = ['plate_number', 'model', 'capacity', 'assigned_route', 'insurance_expiry', 'last_service_date']
    search_fields = ['plate_number', 'model']
    list_filter = ['assigned_route', 'institution']


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(BaseInstitutionAdmin):
    list_display = ['vehicle', 'maintenance_type', 'performed_on', 'cost', 'next_due_date']
    search_fields = ['vehicle__plate_number', 'maintenance_type']
    list_filter = ['performed_on', 'institution']
    date_hierarchy = 'performed_on'


@admin.register(Driver)
class DriverAdmin(BaseInstitutionAdmin):
    list_display = ['user', 'license_number', 'license_expiry', 'assigned_vehicle']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'license_number']
    list_filter = ['license_expiry', 'institution']


@admin.register(TransportBooking)
class TransportBookingAdmin(BaseInstitutionAdmin):
    list_display = ['student', 'travel_date', 'vehicle', 'route', 'pickup_point', 'drop_point', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'pickup_point', 'drop_point']
    list_filter = ['status', 'travel_date', 'institution']
    date_hierarchy = 'travel_date'


@admin.register(TransportAssignment)
class TransportAssignmentAdmin(BaseInstitutionAdmin):
    list_display = ['student', 'route', 'pickup_point', 'drop_point', 'assigned_on', 'is_active']
    search_fields = ['student__first_name', 'student__last_name', 'pickup_point', 'drop_point']
    list_filter = ['is_active', 'assigned_on', 'institution']
    date_hierarchy = 'assigned_on'


@admin.register(TransportAttendance)
class TransportAttendanceAdmin(BaseInstitutionAdmin):
    list_display = ['student', 'date', 'status']
    search_fields = ['student__first_name', 'student__last_name']
    list_filter = ['status', 'institution']
    date_hierarchy = 'date'


@admin.register(VehicleLog)
class VehicleLogAdmin(BaseInstitutionAdmin):
    list_display = ['vehicle', 'date', 'distance_travelled_km', 'fuel_used_litres']
    search_fields = ['vehicle__plate_number']
    list_filter = ['institution']
    date_hierarchy = 'date'


@admin.register(TripLog)
class TripLogAdmin(BaseInstitutionAdmin):
    list_display = ['vehicle', 'route', 'driver', 'start_time', 'end_time', 'status']
    search_fields = ['vehicle__plate_number', 'route__name', 'driver__user__username']
    list_filter = ['status', 'institution']
    date_hierarchy = 'start_time'


@admin.register(TransportNotification)
class TransportNotificationAdmin(BaseInstitutionAdmin):
    list_display = ['student', 'type', 'sent_at', 'is_sent']
    search_fields = ['student__first_name', 'student__last_name', 'message']
    list_filter = ['type', 'is_sent', 'institution']
    date_hierarchy = 'sent_at'
