from django.contrib import admin
from .models import (
    AcademicYear,
    Term,
    HolidayBreak,
    AcademicEvent,
    AcademicAuditLog
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'start_date', 'end_date', 'is_current')
    list_filter = ('institution', 'is_current')
    search_fields = ('name', 'institution__name')
    ordering = ('-start_date',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'start_date', 'end_date', 'is_active')
    list_filter = ('academic_year__institution', 'is_active')
    search_fields = ('name', 'academic_year__name')
    ordering = ('start_date',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(HolidayBreak)
class HolidayBreakAdmin(admin.ModelAdmin):
    list_display = ('title', 'term', 'start_date', 'end_date')
    list_filter = ('term__academic_year__institution',)
    search_fields = ('title', 'term__name')
    ordering = ('start_date',)


@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'institution', 'term', 'start_date', 'end_date', 'is_school_wide')
    list_filter = ('institution', 'term__academic_year', 'is_school_wide')
    search_fields = ('title', 'term__name', 'institution__name')
    ordering = ('start_date',)


@admin.register(AcademicAuditLog)
class AcademicAuditLogAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'action', 'actor', 'timestamp')
    list_filter = ('model_name', 'action', 'timestamp')
    search_fields = ('model_name', 'actor__email', 'record_id')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
