from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    AnnouncementCategory,
    CommunicationAnnouncement,
    CommunicationTarget,
    CommunicationReadLog,
    CommunicationLog
)


@admin.register(AnnouncementCategory)
class AnnouncementCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class CommunicationTargetInline(admin.TabularInline):
    model = CommunicationTarget
    extra = 0


class CommunicationReadLogInline(admin.TabularInline):
    model = CommunicationReadLog
    extra = 0
    readonly_fields = ('user', 'read_at')
    can_delete = False


@admin.register(CommunicationAnnouncement)
class CommunicationAnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'institution', 'category', 'priority', 'is_public',
        'sent', 'scheduled_at', 'created_at', 'expires_at'
    )
    list_filter = ('priority', 'is_public', 'sent', 'category', 'institution')
    search_fields = ('title', 'content', 'author__username', 'institution__name')
    autocomplete_fields = ('author', 'institution', 'category')
    inlines = [CommunicationTargetInline, CommunicationReadLogInline]
    readonly_fields = ('sent', 'created_at', 'updated_at')


@admin.register(CommunicationTarget)
class CommunicationTargetAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'role', 'user', 'class_level', 'stream')
    list_filter = ('role', 'class_level', 'stream')
    search_fields = ('announcement__title', 'user__username')


@admin.register(CommunicationReadLog)
class CommunicationReadLogAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'user', 'read_at')
    search_fields = ('announcement__title', 'user__username')
    list_filter = ('read_at',)
    autocomplete_fields = ('announcement', 'user')


@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('announcement__title', 'details')
    autocomplete_fields = ('announcement',)
