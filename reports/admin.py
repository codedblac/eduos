# reports/admin.py

from django.contrib import admin
from .models import (
    GeneratedReport,
    ReportStudentPerformance,
    ReportSubjectBreakdown,
    ReportAuditTrail,
    ReportPrintRequest
)


class ReportStudentPerformanceInline(admin.TabularInline):
    model = ReportStudentPerformance
    extra = 0
    readonly_fields = ('student', 'mean_score', 'grade', 'rank', 'position_out_of', 'flagged')
    fields = ('student', 'total_marks', 'mean_score', 'grade', 'rank', 'position_out_of', 'flagged', 'comment', 'remedial_suggestion')
    show_change_link = True


class ReportSubjectBreakdownInline(admin.TabularInline):
    model = ReportSubjectBreakdown
    extra = 0
    readonly_fields = ('subject', 'average_score', 'top_score', 'lowest_score', 'pass_rate', 'failure_rate', 'most_common_grade', 'flagged')
    fields = ('subject', 'teacher', 'average_score', 'top_score', 'lowest_score', 'pass_rate', 'failure_rate', 'most_common_grade', 'flagged', 'comment')
    show_change_link = True


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'institution', 'report_type', 'term', 'year', 'access_level', 'date_generated', 'is_auto_generated')
    list_filter = ('institution', 'report_type', 'access_level', 'term', 'year', 'is_auto_generated')
    search_fields = ('title', 'institution__name', 'term', 'year')
    readonly_fields = ('generated_by', 'date_generated', 'updated_at', 'version', 'file', 'json_data')
    inlines = [ReportStudentPerformanceInline, ReportSubjectBreakdownInline]

    fieldsets = (
        ('Report Metadata', {
            'fields': ('title', 'description', 'institution', 'report_type', 'access_level', 'generated_by', 'is_auto_generated')
        }),
        ('Context Info', {
            'fields': ('class_level', 'stream', 'term', 'year')
        }),
        ('Output & AI', {
            'fields': ('file', 'json_data', 'ai_summary', 'smart_flags')
        }),
        ('Versioning', {
            'fields': ('version', 'date_generated', 'updated_at')
        }),
    )


@admin.register(ReportStudentPerformance)
class ReportStudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'report', 'mean_score', 'grade', 'rank', 'flagged')
    list_filter = ('grade', 'flagged', 'class_level', 'stream')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'report__title')
    readonly_fields = ('report',)


@admin.register(ReportSubjectBreakdown)
class ReportSubjectBreakdownAdmin(admin.ModelAdmin):
    list_display = ('subject', 'report', 'teacher', 'average_score', 'pass_rate', 'flagged')
    list_filter = ('subject', 'class_level', 'stream', 'flagged')
    search_fields = ('subject__name', 'teacher__first_name', 'teacher__last_name', 'report__title')
    readonly_fields = ('report',)


@admin.register(ReportAuditTrail)
class ReportAuditTrailAdmin(admin.ModelAdmin):
    list_display = ('report', 'action', 'performed_by', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('report__title', 'performed_by__username', 'performed_by__first_name')
    readonly_fields = ('timestamp',)


@admin.register(ReportPrintRequest)
class ReportPrintRequestAdmin(admin.ModelAdmin):
    list_display = ('report', 'requested_by', 'copies', 'requested_at')
    list_filter = ('requested_at',)
    search_fields = ('report__title', 'requested_by__username')
    readonly_fields = ('requested_at',)
