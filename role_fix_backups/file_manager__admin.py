from django.contrib import admin
from .models import (
    FileCategory, ManagedFile, FileVersion, FileAccessLog,
    SharedAccess, AssignmentSubmission, FileAnalytics, FileComment, FileLock
)


class FileVersionInline(admin.TabularInline):
    model = FileVersion
    extra = 0
    readonly_fields = ('version_number', 'uploaded_by', 'created_at')
    fields = ('version_number', 'file', 'uploaded_by', 'created_at', 'changelog')


class AssignmentSubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0
    readonly_fields = ('submitted_at', 'comment')
    fields = ('student', 'submitted_at', 'comment')


class FileAnalyticsInline(admin.StackedInline):
    model = FileAnalytics
    can_delete = False
    readonly_fields = ('download_count', 'view_count', 'last_accessed')


@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_type', 'uploaded_by', 'institution', 'is_public', 'is_archived', 'created_at')
    list_filter = ('file_type', 'is_public', 'is_archived', 'institution', 'class_level', 'subject')
    search_fields = ('name', 'description', 'tags__name', 'uploaded_by__username')
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'preview_url')
    inlines = [FileVersionInline, AssignmentSubmissionInline, FileAnalyticsInline]
    autocomplete_fields = (
        'uploaded_by', 'modified_by', 'institution',
        'class_level', 'stream', 'subject', 'student'
    )
    # Removed filter_horizontal for 'tags' due to custom through model from taggit
    fieldsets = (
        (None, {
            'fields': ('name', 'file', 'file_type', 'file_size', 'category', 'description')
        }),
        ('Ownership & Scope', {
            'fields': (
                'uploaded_by', 'modified_by', 'institution',
                'class_level', 'stream', 'subject', 'student', 'access_scope'
            )
        }),
        ('Flags & Extras', {
            'fields': (
                'is_public', 'is_archived', 'is_deleted',
                'compressed', 'preview_available', 'preview_url', 'version'
            )
        }),
        ('AI & Metadata', {
            'fields': ('summary', 'keywords', 'is_recommended', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'expires_at')
        }),
    )


@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(FileVersion)
class FileVersionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'version_number', 'uploaded_by', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('managed_file', 'uploaded_by')


@admin.register(FileAccessLog)
class FileAccessLogAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'action', 'accessed_at')
    list_filter = ('action', 'accessed_at')
    search_fields = ('file__name', 'user__username')
    readonly_fields = ('file', 'user', 'action', 'accessed_at')


@admin.register(SharedAccess)
class SharedAccessAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'primary_role', 'can_download', 'can_comment', 'expires_at')
    list_filter = ('can_download', 'can_comment', 'class_level', 'stream')
    autocomplete_fields = ('file', 'user', 'class_level', 'stream')


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('file', 'student', 'submitted_at')
    readonly_fields = ('submitted_at',)
    search_fields = ('file__name', 'student__username')
    autocomplete_fields = ('file', 'student')


@admin.register(FileComment)
class FileCommentAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'created_at')
    search_fields = ('file__name', 'user__username', 'content')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FileLock)
class FileLockAdmin(admin.ModelAdmin):
    list_display = ('file', 'is_locked', 'locked_by', 'locked_at')
    readonly_fields = ('locked_at',)
    autocomplete_fields = ('file', 'locked_by')
