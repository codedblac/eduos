from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    LessonPlan,
    LessonSchedule,
    LessonSession,
    LessonAttachment
)


# Inline for LessonAttachment within LessonSession
class LessonAttachmentInline(admin.TabularInline):
    model = LessonAttachment
    extra = 0
    readonly_fields = ('uploaded_by', 'uploaded_at')


# Inline for LessonSession within LessonSchedule (OneToOne)
class LessonSessionInline(admin.StackedInline):
    model = LessonSession
    extra = 0
    can_delete = False
    show_change_link = True


# Inline for LessonSchedule within LessonPlan
class LessonScheduleInline(admin.TabularInline):
    model = LessonSchedule
    extra = 0
    show_change_link = True


# Admin for LessonPlan
@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'subject', 'class_level', 'teacher', 'term', 'week_number',
        'teaching_method', 'delivery_mode', 'duration_minutes', 'is_approved'
    )
    list_filter = (
        'term', 'class_level', 'subject', 'delivery_mode', 'teaching_method', 'is_approved'
    )
    search_fields = (
        'title', 'objectives', 'subject__name', 'teacher__first_name', 'teacher__last_name'
    )
    ordering = ('term', 'class_level', 'subject', 'week_number')
    inlines = [LessonScheduleInline]
    autocomplete_fields = ('subject', 'class_level', 'teacher', 'topic', 'subtopic')
    readonly_fields = ('created_at', 'updated_at')


# Admin for LessonSchedule
@admin.register(LessonSchedule)
class LessonScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'lesson_plan', 'scheduled_date', 'scheduled_time', 'period', 'status'
    )
    list_filter = (
        'lesson_plan__term', 'lesson_plan__subject', 'status'
    )
    search_fields = (
        'lesson_plan__title', 'period'
    )
    ordering = ('scheduled_date', 'scheduled_time')
    inlines = [LessonSessionInline]
    autocomplete_fields = ('lesson_plan',)


# Admin for LessonSession
@admin.register(LessonSession)
class LessonSessionAdmin(admin.ModelAdmin):
    list_display = (
        'lesson_schedule', 'delivered_on', 'coverage_status', 'is_reviewed', 'recorded_by'
    )
    list_filter = (
        'coverage_status', 'is_reviewed', 'lesson_schedule__lesson_plan__term'
    )
    search_fields = (
        'summary', 'homework', 'challenges_faced', 'recorded_by__email'
    )
    ordering = ('-delivered_on',)
    readonly_fields = ('created_at',)
    inlines = [LessonAttachmentInline]
    autocomplete_fields = ('lesson_schedule', 'recorded_by')


# Admin for LessonAttachment
@admin.register(LessonAttachment)
class LessonAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'lesson_session', 'uploaded_by', 'uploaded_at'
    )
    list_filter = (
        'uploaded_by', 'lesson_session__lesson_schedule__lesson_plan__term'
    )
    search_fields = (
        'title', 'external_link', 'uploaded_by__email'
    )
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)
    autocomplete_fields = ('lesson_session', 'uploaded_by')
