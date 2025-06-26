from django.contrib import admin
from .models import (
    VisitorLog,
    Appointment,
    ParcelDelivery,
    GatePass,
    FrontDeskTicket,
    FrontAnnouncement,
    SecurityLog,
)


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ['name', 'purpose', 'person_to_visit', 'check_in', 'check_out']
    list_filter = ['purpose', 'check_in']
    readonly_fields = ['check_in', 'check_out']
    ordering = ['-check_in']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['visitor_name', 'purpose', 'meeting_with', 'scheduled_time', 'status']
    list_filter = ['status', 'scheduled_time']
    ordering = ['-scheduled_time']
    readonly_fields = []


@admin.register(ParcelDelivery)
class ParcelDeliveryAdmin(admin.ModelAdmin):
    list_display = ['item_description', 'sender', 'received_by', 'received_on', 'picked_up_by', 'picked_up_on', 'status']
    list_filter = ['status', 'received_on']
    ordering = ['-received_on']
    readonly_fields = ['received_on', 'picked_up_on']


@admin.register(GatePass)
class GatePassAdmin(admin.ModelAdmin):
    list_display = ['issued_to_student', 'issued_to_staff', 'reason', 'time_out', 'time_in', 'is_returned']
    list_filter = ['is_returned', 'time_out']
    ordering = ['-time_out']
    readonly_fields = ['time_out', 'time_in']


@admin.register(FrontDeskTicket)
class FrontDeskTicketAdmin(admin.ModelAdmin):
    list_display = ['subject', 'submitted_by', 'category', 'status', 'created_on']
    list_filter = ['status', 'category', 'created_on']
    ordering = ['-created_on']
    readonly_fields = ['created_on']


@admin.register(FrontAnnouncement)
class FrontAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'display_from', 'display_until', 'created_by']
    list_filter = ['display_from', 'display_until']
    ordering = ['-display_from']
    readonly_fields = []


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ['entry_type', 'name_or_plate', 'time_in', 'time_out', 'recorded_by']
    list_filter = ['entry_type', 'time_in']
    ordering = ['-time_in']
    readonly_fields = ['time_in', 'time_out']
