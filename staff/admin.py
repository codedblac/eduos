# staff/admin.py

from django.contrib import admin
from .models import (
    Staff,
    StaffProfile,
    StaffQualification,
    StaffLeave,
    StaffDisciplinaryAction,
    StaffAttendance,
    EmploymentHistory
)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'job_title', 'staff_category', 'institution', 'department', 'is_active', 'date_joined')
    list_filter = ('staff_category', 'institution', 'department', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'job_title', 'phone')
    autocomplete_fields = ('user', 'institution', 'department')
    ordering = ('-date_joined',)

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'gender', 'nationality', 'id_number')
    search_fields = ('user__first_name', 'user__last_name', 'id_number')
    autocomplete_fields = ('user',)

@admin.register(EmploymentHistory)
class EmploymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('staff', 'position', 'department', 'start_date', 'end_date', 'employment_type')
    list_filter = ('employment_type', 'department')
    search_fields = ('staff__user__first_name', 'staff__user__last_name', 'position')
    autocomplete_fields = ('staff', 'department')

@admin.register(StaffQualification)
class StaffQualificationAdmin(admin.ModelAdmin):
    list_display = ('staff', 'qualification', 'institution_name', 'year_awarded')
    list_filter = ('year_awarded',)
    search_fields = ('qualification', 'institution_name', 'staff__user__first_name', 'staff__user__last_name')
    autocomplete_fields = ('staff',)

@admin.register(StaffLeave)
class StaffLeaveAdmin(admin.ModelAdmin):
    list_display = ('staff', 'leave_type', 'start_date', 'end_date', 'is_approved', 'approved_by')
    list_filter = ('leave_type', 'is_approved')
    search_fields = ('staff__user__first_name', 'staff__user__last_name', 'leave_type')
    autocomplete_fields = ('staff', 'approved_by')

@admin.register(StaffDisciplinaryAction)
class StaffDisciplinaryActionAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date_reported', 'is_resolved', 'resolved_by')
    list_filter = ('is_resolved',)
    search_fields = ('staff__user__first_name', 'staff__user__last_name', 'action_taken')
    autocomplete_fields = ('staff', 'resolved_by')

@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('staff__user__first_name', 'staff__user__last_name')
    autocomplete_fields = ('staff',)
