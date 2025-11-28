from django.contrib import admin
from .models import (
    MaintenanceCategory,
    Equipment,
    MaintenanceSchedule,
    MaintenanceAsset,
    MaintenanceRequest,
    MaintenanceLog,
    MaintenanceStaff,
    PreventiveMaintenance,
)

@admin.register(MaintenanceCategory)
class MaintenanceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution')
    search_fields = ('name',)
    list_filter = ('institution',)

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'category', 'status', 'location', 'institution', 'added_on')
    search_fields = ('name', 'serial_number')
    list_filter = ('status', 'institution', 'category')

@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'schedule_type', 'next_due_date', 'last_maintenance_date', 'institution')
    search_fields = ('equipment__name',)
    list_filter = ('schedule_type', 'institution')
    date_hierarchy = 'next_due_date'

@admin.register(MaintenanceAsset)
class MaintenanceAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_tag', 'location', 'category', 'institution')
    search_fields = ('name', 'asset_tag')
    list_filter = ('category', 'institution')

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'requested_by', 'assigned_to', 'requested_at', 'institution')
    search_fields = ('title', 'description')
    list_filter = ('status', 'priority', 'institution')
    date_hierarchy = 'requested_at'

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('maintenance_request', 'performed_by', 'work_done_on', 'cost_incurred', 'institution')
    search_fields = ('maintenance_request__title', 'notes')
    list_filter = ('institution',)
    date_hierarchy = 'work_done_on'

@admin.register(MaintenanceStaff)
class MaintenanceStaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'primary_role', 'specialization', 'is_active', 'institution')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('primary_role', 'is_active', 'institution')

@admin.register(PreventiveMaintenance)
class PreventiveMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('asset', 'schedule_date', 'completed', 'completed_on', 'institution')
    search_fields = ('asset__name',)
    list_filter = ('completed', 'institution')
    date_hierarchy = 'schedule_date'
