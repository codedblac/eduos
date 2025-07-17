from django.contrib import admin
from .models import (
    TransportRoute, RouteStopPoint, Vehicle, MaintenanceRecord, Driver,
    TransportBooking, TransportAssignment, TransportAttendance, VehicleLog,
    TripLog, GPSLog, EmergencyAlert, TransportNotification, TransportFee,
    FeePaymentLog, AIDriverEfficiencyScore, ParentTransportFeedback
)


@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_location', 'end_location', 'institution', 'is_active')
    list_filter = ('institution', 'is_active')
    search_fields = ('name', 'start_location', 'end_location')


@admin.register(RouteStopPoint)
class RouteStopPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'route', 'order')
    list_filter = ('route',)
    search_fields = ('name',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'model', 'capacity', 'assigned_route', 'institution')
    list_filter = ('institution',)
    search_fields = ('plate_number', 'model')


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'maintenance_type', 'performed_on', 'cost', 'institution')
    list_filter = ('maintenance_type', 'performed_on')
    search_fields = ('vehicle__plate_number', 'maintenance_type')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'assigned_vehicle', 'license_expiry', 'institution')
    list_filter = ('institution',)
    search_fields = ('user__username', 'license_number')


@admin.register(TransportBooking)
class TransportBookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'travel_date', 'route', 'vehicle', 'status', 'institution')
    list_filter = ('status', 'travel_date', 'institution')
    search_fields = ('student__user__username', 'pickup_point', 'drop_point')


@admin.register(TransportAssignment)
class TransportAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'route', 'pickup_point', 'drop_point', 'assigned_on', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('student__user__username', 'pickup_point', 'drop_point')


@admin.register(TransportAttendance)
class TransportAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'recorded_by', 'institution')
    list_filter = ('date', 'status', 'institution')
    search_fields = ('student__user__username',)


@admin.register(VehicleLog)
class VehicleLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'date', 'distance_travelled_km', 'fuel_used_litres', 'recorded_by')
    list_filter = ('date', 'institution')
    search_fields = ('vehicle__plate_number',)


@admin.register(TripLog)
class TripLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'route', 'driver', 'start_time', 'end_time', 'status', 'institution')
    list_filter = ('status', 'institution')
    search_fields = ('vehicle__plate_number', 'route__name')


@admin.register(GPSLog)
class GPSLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'timestamp', 'latitude', 'longitude', 'speed_kmh')
    search_fields = ('vehicle__plate_number',)


@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'driver', 'triggered_at', 'resolved')
    list_filter = ('resolved',)
    search_fields = ('vehicle__plate_number', 'driver__user__username')


@admin.register(TransportNotification)
class TransportNotificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'type', 'sent_at', 'is_sent', 'institution')
    list_filter = ('type', 'is_sent', 'institution')
    search_fields = ('student__user__username', 'message')


@admin.register(TransportFee)
class TransportFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'route', 'amount', 'term', 'year', 'status')
    list_filter = ('status', 'term', 'year')
    search_fields = ('student__user__username',)


@admin.register(FeePaymentLog)
class FeePaymentLogAdmin(admin.ModelAdmin):
    list_display = ('fee', 'paid_on', 'amount_paid', 'recorded_by')
    list_filter = ('paid_on',)
    search_fields = ('fee__student__user__username',)


@admin.register(AIDriverEfficiencyScore)
class AIDriverEfficiencyScoreAdmin(admin.ModelAdmin):
    list_display = ('driver', 'score', 'calculated_at')
    list_filter = ('calculated_at',)
    search_fields = ('driver__user__username',)


@admin.register(ParentTransportFeedback)
class ParentTransportFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'rating', 'submitted_at')
    list_filter = ('submitted_at', 'rating')
    search_fields = ('student__user__username', 'comment')
