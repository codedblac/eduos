from django.contrib import admin
from .models import (
    PeriodTemplate, Room, SubjectAssignment, TimetableVersion,
    TimetableEntry, TimetableNotificationSetting,
    TimetableChangeLog, TeacherAvailabilityOverride
)


@admin.register(PeriodTemplate)
class PeriodTemplateAdmin(admin.ModelAdmin):
    list_display = ('institution', 'class_level', 'day', 'period_number', 'start_time', 'end_time')
    list_filter = ('institution', 'class_level', 'day')
    search_fields = ('institution__name', 'class_level__name')
    ordering = ('class_level', 'day', 'period_number')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_lab', 'institution')
    list_filter = ('is_lab', 'institution')
    search_fields = ('name', 'institution__name')
    ordering = ('institution', 'name')


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'stream', 'lessons_per_week', 'is_substitutable', 'institution')
    list_filter = ('institution', 'subject', 'stream', 'teacher', 'is_substitutable')
    search_fields = (
        'teacher__user__first_name', 'teacher__user__last_name',
        'subject__name', 'stream__name', 'institution__name'
    )
    autocomplete_fields = ('teacher', 'subject', 'stream', 'institution')
    ordering = ('institution', 'stream', 'subject')


@admin.register(TimetableVersion)
class TimetableVersionAdmin(admin.ModelAdmin):
    list_display = ('institution', 'term', 'academic_year', 'is_finalized', 'created_at')
    list_filter = ('institution', 'term', 'is_finalized')
    search_fields = ('institution__name',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('period_template', 'stream', 'subject', 'teacher', 'room', 'version')
    list_filter = ('version__institution', 'period_template__day', 'subject', 'teacher', 'stream')
    search_fields = (
        'stream__name', 'subject__name', 'teacher__user__first_name',
        'teacher__user__last_name', 'room__name', 'version__institution__name'
    )
    autocomplete_fields = ('version', 'period_template', 'stream', 'subject', 'teacher', 'room')
    ordering = ('period_template__day', 'period_template__start_time')
    date_hierarchy = 'created_at'
    list_per_page = 25


@admin.register(TimetableNotificationSetting)
class TimetableNotificationSettingAdmin(admin.ModelAdmin):
    list_display = ('institution', 'daily_overview_enabled', 'reminder_lead_time_minutes')
    list_filter = ('daily_overview_enabled',)
    search_fields = ('institution__name',)


@admin.register(TimetableChangeLog)
class TimetableChangeLogAdmin(admin.ModelAdmin):
    list_display = ('entry', 'change_type', 'changed_by', 'timestamp')
    list_filter = ('change_type', 'timestamp')
    search_fields = (
        'entry__stream__name', 'entry__subject__name',
        'changed_by__first_name', 'changed_by__last_name'
    )
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)


@admin.register(TeacherAvailabilityOverride)
class TeacherAvailabilityOverrideAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'allowed_to_substitute', 'stream')
    list_filter = ('allowed_to_substitute', 'teacher', 'date')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name', 'stream__name')
    ordering = ('-date',)
