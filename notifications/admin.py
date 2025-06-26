from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Notification, NotificationDelivery, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'institution', 'created_by', 'created_at', 'is_active')
    list_filter = ('notification_type', 'institution', 'is_active', 'channels')
    search_fields = ('title', 'message', 'created_by__email')
    filter_horizontal = (
        'target_users',
        'target_students',
        'target_class_levels',
        'target_streams',
    )
    readonly_fields = ('created_by', 'created_at')
    fieldsets = (
        ("Content", {
            "fields": ("title", "message", "notification_type", "channels", "is_active")
        }),
        ("Targeting", {
            "fields": (
                "target_roles", "target_users", "target_students",
                "target_class_levels", "target_streams"
            )
        }),
        ("Meta", {
            "fields": ("institution", "created_by", "created_at")
        })
    )


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = ('notification', 'user', 'channel', 'delivered', 'read', 'delivered_at', 'read_at')
    list_filter = ('delivered', 'read', 'channel')
    search_fields = ('notification__title', 'user__email')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'allow_email', 'allow_sms', 'allow_push', 'allow_in_app')
    list_filter = ('allow_email', 'allow_sms', 'allow_push', 'allow_in_app')
    search_fields = ('user__email',)
