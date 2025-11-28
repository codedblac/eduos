from django.contrib import admin
from .models import (
    Department, DepartmentUser, DepartmentRoleAssignmentHistory,
    Subject, DepartmentAnnouncement, DepartmentPerformanceNote,
    DepartmentLeaveApproval, DepartmentMeeting, DepartmentKPI,
    DepartmentBudget, DepartmentResource, DepartmentAuditLog,
    DepartmentDocument, DepartmentGoal, DepartmentAnnualPlan,
    DepartmentTask, DepartmentAnalyticsSnapshot
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'type', 'is_academic', 'created_at')
    list_filter = ('institution', 'type', 'is_academic')
    search_fields = ('name', 'code', 'institution__name')


@admin.register(DepartmentUser)
class DepartmentUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'primary_role', 'is_active', 'assigned_on')
    list_filter = ('primary_role', 'is_active', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'assigned_teacher', 'is_examable')
    list_filter = ('department', 'is_examable', 'is_mapped_to_timetable')
    search_fields = ('name', 'code', 'department__name')


@admin.register(DepartmentBudget)
class DepartmentBudgetAdmin(admin.ModelAdmin):
    list_display = ('department', 'fiscal_year', 'amount_allocated', 'amount_used')
    list_filter = ('fiscal_year', 'department')
    search_fields = ('department__name',)


@admin.register(DepartmentKPI)
class DepartmentKPIAdmin(admin.ModelAdmin):
    list_display = ('department', 'term', 'target', 'reviewed_by', 'reviewed_at')
    list_filter = ('term', 'department')
    search_fields = ('target',)



admin.site.register(DepartmentRoleAssignmentHistory)
admin.site.register(DepartmentAnnouncement)
admin.site.register(DepartmentPerformanceNote)
admin.site.register(DepartmentLeaveApproval)
admin.site.register(DepartmentMeeting)
admin.site.register(DepartmentResource)
admin.site.register(DepartmentAuditLog)
admin.site.register(DepartmentDocument)
admin.site.register(DepartmentGoal)
admin.site.register(DepartmentAnnualPlan)
admin.site.register(DepartmentTask)
admin.site.register(DepartmentAnalyticsSnapshot)
