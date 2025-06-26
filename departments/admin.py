from django.contrib import admin
from .models import (
    Department,
    DepartmentUser,
    Subject,
    DepartmentAnnouncement,
    DepartmentPerformanceNote,
    DepartmentLeaveApproval
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'institution', 'type', 'is_academic', 'created_at')
    list_filter = ('institution', 'type', 'is_academic')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)


@admin.register(DepartmentUser)
class DepartmentUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'role', 'is_active', 'assigned_on')
    list_filter = ('role', 'is_active', 'department__institution')
    search_fields = ('user__first_name', 'user__last_name', 'department__name')
    ordering = ('department', 'role')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'department',
        'assigned_teacher',
        'is_examable',
        'is_mapped_to_timetable',
        'is_linked_to_elearning'
    )
    list_filter = ('is_examable', 'is_mapped_to_timetable', 'is_linked_to_elearning', 'department__institution')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)


@admin.register(DepartmentAnnouncement)
class DepartmentAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'created_by', 'created_at')
    list_filter = ('department__institution', 'created_at')
    search_fields = ('title', 'message')
    ordering = ('-created_at',)


@admin.register(DepartmentPerformanceNote)
class DepartmentPerformanceNoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'department', 'created_by', 'approved_by', 'created_at', 'approved')
    list_filter = ('approved', 'department__institution', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'note')
    ordering = ('-created_at',)


@admin.register(DepartmentLeaveApproval)
class DepartmentLeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ('staff_member', 'department', 'status', 'requested_at', 'approved_by', 'decision_date')
    list_filter = ('status', 'department__institution', 'requested_at')
    search_fields = ('staff_member__first_name', 'staff_member__last_name', 'reason')
    ordering = ('-requested_at',)
