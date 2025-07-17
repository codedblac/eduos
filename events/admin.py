from django.contrib import admin
from .models import (
    EventType, RecurringEventRule, EventTag, EventAttachment,
    Event, EventRSVP, EventAttendance, EventFeedback, EventComment
)


@admin.register(RecurringEventRule)
class RecurringEventRuleAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'interval', 'end_date', 'created_at')
    list_filter = ('frequency',)
    search_fields = ('frequency',)


@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)


@admin.register(EventAttachment)
class EventAttachmentAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_by', 'uploaded_at', 'description')
    search_fields = ('description',)
    list_filter = ('uploaded_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'event_type', 'institution', 'start_time', 'end_time',
        'is_virtual', 'is_all_day', 'is_recurring', 'is_active'
    )
    list_filter = ('event_type', 'is_virtual', 'is_all_day', 'is_recurring', 'is_active')
    search_fields = ('title', 'description', 'location')
    filter_horizontal = (
        'tags', 'media_attachments', 'target_users',
        'target_students', 'target_class_levels', 'target_streams'
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EventRSVP)
class EventRSVPAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'response', 'responded_at')
    list_filter = ('response',)
    search_fields = ('event__title', 'user__username')


@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'is_present', 'timestamp', 'recorded_by')
    list_filter = ('is_present',)
    search_fields = ('event__title', 'user__username', 'recorded_by__username')


@admin.register(EventFeedback)
class EventFeedbackAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating', 'submitted_at')
    list_filter = ('rating',)
    search_fields = ('event__title', 'user__username', 'comment')


@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'comment', 'created_at', 'edited_at')
    search_fields = ('event__title', 'user__username', 'comment')
    list_filter = ('created_at',)


# Optional: unregister models if they were already auto-registered
# admin.site.unregister(SomeModel)
