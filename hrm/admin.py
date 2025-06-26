from django.contrib import admin
from .models import (
    SchoolBranch, Department, HRMLog, JobPosting, JobApplication, StaffHRRecord,
    Contract, HRDocument, LeaveType, LeaveRequest, AttendanceRecord,
    PerformanceReview, DisciplinaryAction, HRAuditLog
)


@admin.register(SchoolBranch)
class SchoolBranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'location']
    search_fields = ['name', 'institution__name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'head']
    search_fields = ['name', 'branch__name', 'head__username']


@admin.register(HRMLog)
class HRMLogAdmin(admin.ModelAdmin):
    list_display = ['staff', 'actor', 'action', 'category', 'timestamp']
    list_filter = ['category', 'timestamp']
    search_fields = ['staff__user__username', 'actor__username', 'action']


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'is_internal', 'posted_on', 'deadline']
    list_filter = ['is_internal']
    search_fields = ['title', 'department__name']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant_name', 'email', 'job', 'status', 'applied_on']
    list_filter = ['status']
    search_fields = ['applicant_name', 'email', 'job__title']


@admin.register(StaffHRRecord)
class StaffHRRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'institution', 'branch', 'department', 'designation', 'status', 'date_joined']
    list_filter = ['status', 'institution', 'branch', 'department']
    search_fields = ['user__username', 'employee_id', 'designation']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['staff', 'contract_type', 'start_date', 'end_date', 'is_active']
    list_filter = ['contract_type', 'is_active']
    search_fields = ['staff__user__username', 'staff__employee_id']


@admin.register(HRDocument)
class HRDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'staff', 'uploaded_at']
    search_fields = ['title', 'staff__user__username']


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'start_date', 'end_date', 'status', 'requested_on']
    list_filter = ['status', 'leave_type']
    search_fields = ['staff__user__username']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'check_in', 'check_out', 'method']
    list_filter = ['date', 'method']
    search_fields = ['staff__user__username']


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ['staff', 'reviewer', 'review_period_start', 'review_period_end', 'score', 'submitted_on']
    list_filter = ['submitted_on']
    search_fields = ['staff__user__username', 'reviewer__username']


@admin.register(DisciplinaryAction)
class DisciplinaryActionAdmin(admin.ModelAdmin):
    list_display = ['staff', 'incident_date', 'resolved', 'added_by']
    list_filter = ['resolved']
    search_fields = ['staff__user__username', 'added_by__username']


@admin.register(HRAuditLog)
class HRAuditLogAdmin(admin.ModelAdmin):
    list_display = ['staff', 'action', 'performed_by', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['staff__user__username', 'performed_by__username', 'action']
