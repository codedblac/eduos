from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    SchoolAttendanceRecord,
    ClassAttendanceRecord,
    AbsenceReason
)


@admin.register(SchoolAttendanceRecord)
class SchoolAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'institution', 'date',
        'entry_time', 'exit_time', 'source',
        'recorded_by', 'recorded_at'
    )
    list_filter = ('institution', 'date', 'source')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('recorded_by', 'recorded_at')


@admin.register(ClassAttendanceRecord)
class ClassAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'get_person', 'institution', 'date', 'status',
        'subject', 'class_level', 'stream',
        'timetable_entry', 'source', 'recorded_by'
    )
    list_filter = (
        'institution', 'date', 'status', 'source',
        'class_level', 'stream', 'subject'
    )
    search_fields = (
        'student__user__email', 'student__user__first_name',
        'teacher__email', 'teacher__first_name'
    )
    readonly_fields = ('recorded_by', 'recorded_at')

    def get_person(self, obj):
        return obj.student or obj.teacher
    get_person.short_description = "Student/Teacher"


@admin.register(AbsenceReason)
class AbsenceReasonAdmin(admin.ModelAdmin):
    list_display = ('reason', 'institution', 'default')
    list_filter = ('institution', 'default')
    search_fields = ('reason',)
