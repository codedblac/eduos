from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    AcademicYear,
    Term,
    HolidayBreak,
    AcademicEvent,
    AcademicAuditLog
)


# --- Inline for Breaks within Term ---
class HolidayBreakInline(admin.TabularInline):
    model = HolidayBreak
    extra = 0


# --- Inline for Terms within Academic Year ---
class TermInline(admin.TabularInline):
    model = Term
    extra = 0
    show_change_link = True


# --- Academic Year Admin ---
@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'start_date', 'end_date', 'is_current', 'created_at')
    list_filter = ('institution', 'is_current')
    search_fields = ('name', 'institution__name')
    ordering = ('-start_date',)
    inlines = [TermInline]
    readonly_fields = ('created_at',)


# --- Term Admin ---
@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'start_date', 'end_date', 'is_active', 'midterm_date')
    list_filter = ('academic_year__institution', 'academic_year', 'is_active')
    search_fields = ('name', 'academic_year__name')
    ordering = ('start_date',)
    inlines = [HolidayBreakInline]
    readonly_fields = ('created_at',)


# --- Holiday Break Admin ---
@admin.register(HolidayBreak)
class HolidayBreakAdmin(admin.ModelAdmin):
    list_display = ('title', 'term', 'start_date', 'end_date')
    list_filter = ('term__academic_year__institution', 'term')
    search_fields = ('title', 'description')
    ordering = ('start_date',)


# --- Academic Event Admin ---
@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'term', 'academic_year', 'institution', 'start_date', 'end_date', 'is_school_wide')
    list_filter = ('institution', 'academic_year', 'term', 'is_school_wide')
    search_fields = ('title', 'description')
    ordering = ('start_date',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'institution', 'academic_year', 'term', 'start_date', 'end_date', 'is_school_wide', 'color_code')
        }),
    )


# --- Academic Audit Log Admin ---
@admin.register(AcademicAuditLog)
class AcademicAuditLogAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'action', 'actor', 'timestamp', 'record_id')
    list_filter = ('action', 'model_name', 'actor')
    search_fields = ('model_name', 'notes', 'actor__email')
    ordering = ('-timestamp',)
    readonly_fields = ('actor', 'action', 'model_name', 'record_id', 'timestamp', 'notes')
