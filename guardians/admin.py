from django.contrib import admin
from .models import Guardian, GuardianStudentLink, GuardianNotification

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ['user', 'institution', 'phone_number', 'occupation', 'is_active']
    search_fields = ['user__username', 'user__email']

@admin.register(GuardianStudentLink)
class GuardianStudentLinkAdmin(admin.ModelAdmin):
    list_display = ['guardian', 'student', 'relationship', 'is_primary']

@admin.register(GuardianNotification)
class GuardianNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'guardian', 'type', 'is_read', 'timestamp']
    list_filter = ['type', 'is_read']
