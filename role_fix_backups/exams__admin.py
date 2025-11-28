from django.contrib import admin

# Register your models here.
# exams/admin.py

from django.contrib import admin
from .models import Exam, ExamResult
from import_export.admin import ExportMixin
from import_export import resources
from .models import (
    Exam,
    ExamSubject,
    ExamResult,
    StudentScore,
    GradeBoundary,
    ExamInsight,
    ExamPrediction,
)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_level', 'stream', 'term', 'year', 'institution', 'created_by', 'created_at']
    list_filter = ['term', 'year', 'institution', 'class_level', 'stream']
    search_fields = [ 'class_level__name', 'stream__name', 'institution__name']
    ordering = ['-year', 'term', 'name']
    autocomplete_fields = ['class_level', 'stream', 'institution', 'created_by']


@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ['exam', 'subject', 'max_score']
    list_filter = ['exam__term', 'exam__year', 'subject']
    search_fields = ['exam__name', 'subject__name']
    ordering = ['exam', 'subject']
    autocomplete_fields = ['exam', 'subject']


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'total_score', 'average_score', 'grade', 'overall_position']
    list_filter = ['exam__term', 'exam__year', 'grade']
    search_fields = ['student__first_name', 'student__last_name', 'exam__name']
    ordering = ['-average_score']
    autocomplete_fields = ['exam', 'student']


@admin.register(StudentScore)
class StudentScoreAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam_subject', 'score', 'grade', 'position']
    list_filter = ['grade', 'exam_subject__exam__term', 'exam_subject__exam__year']
    search_fields = ['student__first_name', 'student__last_name', 'exam_subject__subject__name']
    ordering = ['-score']
    autocomplete_fields = ['exam_subject', 'student']


@admin.register(GradeBoundary)
class GradeBoundaryAdmin(admin.ModelAdmin):
    list_display = ['institution', 'subject', 'grade', 'min_score', 'max_score']
    list_filter = ['institution', 'subject', 'grade']
    search_fields = ['institution__name', 'subject__name', 'grade']
    ordering = ['-min_score']
    autocomplete_fields = ['institution', 'subject']


@admin.register(ExamInsight)
class ExamInsightAdmin(admin.ModelAdmin):
    list_display = ['exam', 'subject', 'average_score', 'highest_score', 'lowest_score', 'most_common_grade', 'generated_at']
    list_filter = ['exam__term', 'exam__year', 'subject']
    search_fields = ['exam__name', 'subject__name']
    ordering = ['-generated_at']
    autocomplete_fields = ['exam', 'subject']


@admin.register(ExamPrediction)
class ExamPredictionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'class_level', 'stream', 'term', 'year', 'institution', 'created_by', 'created_at']
    list_filter = ['term', 'year', 'institution', 'class_level', 'stream']
    search_fields = ['subject__name', 'class_level__name', 'stream__name', 'institution__name']
    ordering = ['-created_at']
    autocomplete_fields = ['subject', 'class_level', 'stream', 'institution', 'created_by']