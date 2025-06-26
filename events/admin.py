from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Event, EventTag, EventAttachment, EventRSVP,
    EventAttendance, EventFeedback, RecurringEventRule
)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'event_type', 'institution', 'start_time', 'end_time',
        'is_virtual', 'is_recurring', 'requires_rsvp', 'is_active'
    )
    list_filter = (
        'event_type', 'is_virtual', 'is_recurring', 'is_active',
        'start_time', 'institution'
    )
    search_fields = ['title', 'description']
    date_hierarchy = 'start_time'
    filter_horizontal = (
        'media_attachments', 'tags',
        'target_users', 'target_students',
        'target_class_levels', 'target_streams'
    )
    readonly_fields = ['created_at']
    autocomplete_fields = ['created_by', 'institution']
    fieldsets = (
        ("Basic Info", {
            "fields": (
                'title', 'description', 'event_type', 'institution',
                'start_time', 'end_time', 'is_all_day', 'location',
                'is_virtual', 'virtual_link'
            )
        }),
        ("Advanced Targeting", {
            "fields": (
                'target_roles', 'target_users', 'target_students',
                'target_class_levels', 'target_streams'
            )
        }),
        ("Recurrence & Media", {
            "fields": (
                'is_recurring', 'recurring_rule', 'media_attachments', 'tags'
            )
        }),
        ("RSVP & Feedback", {
            "fields": (
                'requires_rsvp', 'allow_feedback', 'is_active'
            )
        }),
        ("Metadata", {
            "fields": ('created_by', 'created_at')
        })
    )


@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']


@admin.register(EventAttachment)
class EventAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file', 'uploaded_by', 'uploaded_at']
    autocomplete_fields = ['uploaded_by']


@admin.register(EventRSVP)
class EventRSVPAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'response', 'responded_at']
    list_filter = ['response', 'event__title']
    search_fields = ['user__full_name', 'event__title']
    autocomplete_fields = ['event', 'user']


@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'is_present', 'timestamp']
    list_filter = ['is_present']
    search_fields = ['user__full_name', 'event__title']
    autocomplete_fields = ['event', 'user']


@admin.register(EventFeedback)
class EventFeedbackAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'rating', 'submitted_at']
    list_filter = ['rating']
    search_fields = ['user__full_name', 'event__title']
    autocomplete_fields = ['event', 'user']


@admin.register(RecurringEventRule)
class RecurringEventRuleAdmin(admin.ModelAdmin):
    list_display = ['frequency', 'interval', 'end_date']
