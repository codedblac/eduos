from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    GeneratedReport,
    ReportStudentPerformance,
    ReportSubjectBreakdown
)


class ReportStudentPerformanceInline(admin.TabularInline):
    model = ReportStudentPerformance
    extra = 0
    readonly_fields = ['student', 'mean_score', 'grade', 'rank', 'position_out_of']
    show_change_link = False


class ReportSubjectBreakdownInline(admin.TabularInline):
    model = ReportSubjectBreakdown
    extra = 0
    readonly_fields = [
        'subject', 'teacher', 'average_score', 'top_score',
        'lowest_score', 'pass_rate', 'failure_rate', 'most_common_grade'
    ]
    show_change_link = False


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'report_type', 'institution', 'term', 'year',
        'class_level', 'stream', 'access_level', 'date_generated'
    ]
    list_filter = ['report_type', 'access_level', 'institution', 'class_level', 'stream', 'term', 'year']
    search_fields = ['title', 'description']
    readonly_fields = ['generated_by', 'date_generated', 'is_auto_generated', 'json_data']
    inlines = [ReportStudentPerformanceInline, ReportSubjectBreakdownInline]


@admin.register(ReportStudentPerformance)
class ReportStudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'grade', 'rank', 'mean_score', 'report']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    list_filter = ['class_level', 'stream']


@admin.register(ReportSubjectBreakdown)
class ReportSubjectBreakdownAdmin(admin.ModelAdmin):
    list_display = ['subject', 'teacher', 'average_score', 'top_score', 'failure_rate', 'report']
    list_filter = ['class_level', 'stream', 'subject']
    search_fields = ['subject__name', 'teacher__first_name', 'teacher__last_name']
