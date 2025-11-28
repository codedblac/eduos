from django.contrib import admin
from .models import (
    LessonPlan,
    LessonSchedule,
    LessonSession,
    LessonAttachment,
    LessonFeedback,
    LessonTemplate,
    LessonScaffoldSuggestion
)


@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = (
        'subject', 'class_level', 'teacher', 'week_number', 'term',
        'is_approved', 'is_draft', 'version'
    )
    list_filter = ('term', 'subject', 'class_level', 'is_approved', 'is_draft')
    search_fields = ('title', 'summary', 'objectives', 'teacher__username')
    ordering = ('term', 'class_level', 'subject', 'week_number')


@admin.register(LessonSchedule)
class LessonScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'lesson_plan', 'scheduled_date', 'scheduled_time', 'period', 'status'
    )
    list_filter = ('scheduled_date', 'status')
    search_fields = ('lesson_plan__subject__name', 'lesson_plan__teacher__username')
    ordering = ('scheduled_date', 'scheduled_time')


@admin.register(LessonSession)
class LessonSessionAdmin(admin.ModelAdmin):
    list_display = (
        'lesson_schedule', 'delivered_on', 'coverage_status',
        'is_reviewed', 'recorded_by'
    )
    list_filter = ('coverage_status', 'is_reviewed')
    search_fields = ('lesson_schedule__lesson_plan__subject__name',)
    ordering = ('-delivered_on',)


@admin.register(LessonAttachment)
class LessonAttachmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson_session', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'lesson_session__lesson_schedule__lesson_plan__subject__name')
    list_filter = ('uploaded_at',)


@admin.register(LessonFeedback)
class LessonFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'lesson_session', 'submitted_by', 'primary_role', 'rating', 'submitted_at'
    )
    list_filter = ('primary_role', 'submitted_at')
    search_fields = ('comment', 'submitted_by__username', 'lesson_session__lesson_schedule__lesson_plan__subject__name')


@admin.register(LessonTemplate)
class LessonTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'created_by', 'created_at')
    search_fields = ('title', 'summary', 'objectives')
    list_filter = ('delivery_mode', 'teaching_method', 'created_at')


@admin.register(LessonScaffoldSuggestion)
class LessonScaffoldSuggestionAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'created_by', 'created_at')
    search_fields = ('suggestion', 'created_by__username')
    list_filter = ('created_at',)
