from django.contrib import admin
from .models import Guardian, GuardianStudentLink, GuardianNotification

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'institution', 'phone_number', 'email', 'id_number', 'is_active')
    list_filter = ('institution', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'phone_number', 'email', 'id_number')
    ordering = ('user__last_name', 'user__first_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GuardianStudentLink)
class GuardianStudentLinkAdmin(admin.ModelAdmin):
    list_display = ('guardian', 'student', 'relationship', 'is_primary')
    list_filter = ('relationship', 'is_primary', 'guardian__institution')
    search_fields = ('guardian__user__first_name', 'guardian__user__last_name', 'student__first_name', 'student__last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GuardianNotification)
class GuardianNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'guardian', 'type', 'is_read', 'timestamp')
    list_filter = ('type', 'is_read', 'institution')
    search_fields = ('title', 'message', 'guardian__user__first_name', 'guardian__user__last_name')
    readonly_fields = ('timestamp',)
