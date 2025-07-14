from django.contrib import admin
from .models import (
    LessonPlan, LessonSchedule, LessonSession,
    LessonAttachment, LessonFeedback, LessonTemplate
)


@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_level', 'teacher', 'week_number', 'term', 'is_approved', 'created_at')
    list_filter = ('term', 'subject', 'class_level', 'teacher', 'is_approved', 'teaching_method', 'delivery_mode')
    search_fields = ('title', 'objectives', 'activities', 'assessments')
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
    date_hierarchy = 'created_at'


@admin.register(LessonSchedule)
class LessonScheduleAdmin(admin.ModelAdmin):
    list_display = ('lesson_plan', 'scheduled_date', 'scheduled_time', 'period', 'status')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('lesson_plan__title', 'period')
    date_hierarchy = 'scheduled_date'


@admin.register(LessonSession)
class LessonSessionAdmin(admin.ModelAdmin):
    list_display = ('lesson_schedule', 'delivered_on', 'coverage_status', 'is_reviewed', 'recorded_by')
    list_filter = ('coverage_status', 'is_reviewed', 'delivered_on')
    search_fields = ('summary', 'teacher_reflection', 'challenges_faced')
    readonly_fields = ('created_at',)


@admin.register(LessonAttachment)
class LessonAttachmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson_session', 'uploaded_by', 'uploaded_at')
    search_fields = ('title',)
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at',)


@admin.register(LessonFeedback)
class LessonFeedbackAdmin(admin.ModelAdmin):
    list_display = ('lesson_session', 'submitted_by', 'role', 'rating', 'submitted_at')
    list_filter = ('role', 'submitted_at')
    search_fields = ('comment',)
    readonly_fields = ('submitted_at',)


@admin.register(LessonTemplate)
class LessonTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'institution', 'created_by', 'created_at')
    list_filter = ('subject', 'institution', 'teaching_method', 'delivery_mode')
    search_fields = ('title', 'objectives', 'activities', 'assessments')
    readonly_fields = ('created_at',)
