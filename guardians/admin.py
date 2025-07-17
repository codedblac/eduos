from django.contrib import admin
from django.utils.html import format_html
from .models import Guardian, GuardianStudentLink, GuardianNotification

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'institution', 'phone_number', 'email', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number', 'email')
    list_filter = ('institution', 'is_active')
    ordering = ('user__last_name',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 30

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = "Guardian"

@admin.register(GuardianStudentLink)
class GuardianStudentLinkAdmin(admin.ModelAdmin):
    list_display = ('guardian_name', 'student_name', 'relationship', 'is_primary', 'created_at')
    list_filter = ('relationship', 'is_primary')
    search_fields = ('guardian__user__username', 'guardian__user__first_name', 'guardian__user__last_name', 'student__first_name', 'student__last_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-is_primary', 'relationship')

    def guardian_name(self, obj):
        return obj.guardian.user.get_full_name()
    guardian_name.short_description = "Guardian"

    def student_name(self, obj):
        return obj.student.get_full_name()
    student_name.short_description = "Student"

@admin.register(GuardianNotification)
class GuardianNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'guardian_username', 'type', 'is_read', 'timestamp')
    list_filter = ('type', 'is_read', 'timestamp')
    search_fields = ('title', 'message', 'guardian__user__username', 'guardian__user__first_name', 'guardian__user__last_name')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    list_per_page = 25

    def guardian_username(self, obj):
        return obj.guardian.user.username
    guardian_username.short_description = "Guardian"
