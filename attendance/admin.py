from django.contrib import admin
from .models import (
    SchoolAttendanceRecord,
    ClassAttendanceRecord,
    AbsenceReason
)


@admin.register(SchoolAttendanceRecord)
class SchoolAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'user_display', 'institution', 'date',
        'entry_time', 'exit_time', 'source',
        'recorded_by', 'recorded_at'
    )
    list_filter = ('institution', 'date', 'source')
    search_fields = (
        'user__username', 'user__email',
        'user__first_name', 'user__last_name'
    )
    readonly_fields = ('recorded_by', 'recorded_at')
    date_hierarchy = 'date'
    ordering = ['-date']

    def user_display(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.username})"
    user_display.short_description = "User"


@admin.register(ClassAttendanceRecord)
class ClassAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'person_display', 'institution', 'date', 'status',
        'subject', 'class_level', 'stream',
        'timetable_entry', 'source', 'recorded_by'
    )
    list_filter = (
        'institution', 'date', 'status', 'source',
        'class_level', 'stream', 'subject'
    )
    search_fields = (
        'student__user__username', 'student__user__first_name', 'student__user__last_name',
        'teacher__username', 'teacher__first_name', 'teacher__last_name'
    )
    readonly_fields = ('recorded_by', 'recorded_at')
    date_hierarchy = 'date'
    ordering = ['-date']

    def person_display(self, obj):
        if obj.student:
            return f"Student: {obj.student.full_name}"
        elif obj.teacher:
            return f"Teacher: {obj.teacher.get_full_name()}"
        return "N/A"
    person_display.short_description = "Participant"


@admin.register(AbsenceReason)
class AbsenceReasonAdmin(admin.ModelAdmin):
    list_display = ('reason', 'institution', 'default')
    list_filter = ('institution', 'default')
    search_fields = ('reason',)
    ordering = ['reason']
