from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    ELibraryResource,
    ELibraryCategory,
    ELibraryTag,
    ResourceViewLog,
    ResourceVersion
)
from .ai import ELibraryAIEngine


@admin.register(ELibraryCategory)
class ELibraryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 25


class ELibraryResourceCategoryInline(admin.TabularInline):
    model = ELibraryResource.category.through
    extra = 1


@admin.action(description="Mark selected resources as public")
def make_public(modeladmin, request, queryset):
    updated = queryset.update(visibility='all')  # 'all' matches your model VISIBILITY_CHOICES
    modeladmin.message_user(request, f"{updated} resource(s) marked as public.")


@admin.action(description="Mark selected resources as institution-only")
def make_institution_only(modeladmin, request, queryset):
    updated = queryset.update(visibility='students')  # example institution-level visibility
    modeladmin.message_user(request, f"{updated} resource(s) marked as institution-only.")


@admin.action(description="🧠 Auto-Tag Resources with AI")
def auto_tag_with_ai(modeladmin, request, queryset):
    tagged = 0
    for resource in queryset:
        # Fix the AI engine call to pass resource title and description
        new_tags = ELibraryAIEngine.detect_content_topics(resource.title, resource.description)
        if new_tags:
            resource.ai_tags = ', '.join(new_tags) if isinstance(new_tags, list) else new_tags
            resource.save(update_fields=['ai_tags'])
            tagged += 1
    modeladmin.message_user(request, f"{tagged} resource(s) successfully tagged with AI.")


@admin.action(description="✨ Generate AI Recommendations")
def generate_recommendations(modeladmin, request, queryset):
    user = request.user
    recommendations = ELibraryAIEngine.recommend_resources_for_user(user)
    for resource in queryset:
        rec_titles = ', '.join([rec['title'] for rec in recommendations])
        modeladmin.message_user(
            request,
            f"Recommendations for '{resource.title}': {rec_titles}"
        )


@admin.register(ELibraryResource)
class ELibraryResourceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'uploader',
        'institution',
        'visibility',
        'file_size',
        'file_extension',
        'created_at',
        'preview_link',
        'ai_metadata_preview',
    )
    list_filter = ('visibility', 'institution', 'category')
    search_fields = ('title', 'author', 'description', 'tags', 'ai_tags')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'ai_metadata_preview', 'preview_link')
    list_per_page = 30

    actions = [
        make_public,
        make_institution_only,
        auto_tag_with_ai,
        generate_recommendations
    ]

    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'description', 'institution', 'visibility', 'uploaded_by')
        }),
        ('File Details', {
            'fields': ('file', 'file_size', 'file_extension', 'preview_link'),
            'classes': ('collapse',),
        }),
        ('Categories', {
            'fields': ('category',),
            'classes': ('collapse',),
        }),
        ('AI Metadata', {
            'fields': ('ai_tags', 'ai_metadata_preview'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    inlines = [ELibraryResourceCategoryInline]

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    def file_size(self, obj):
        try:
            size = obj.file.size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size / 1024:.2f} KB"
            else:
                return f"{size / (1024 * 1024):.2f} MB"
        except Exception:
            return "N/A"
    file_size.short_description = 'File Size'

    def file_extension(self, obj):
        try:
            return obj.file.name.split('.')[-1].upper()
        except Exception:
            return "N/A"
    file_extension.short_description = 'File Ext.'

    def ai_metadata_preview(self, obj):
        if not obj.ai_tags:
            return format_html('<em>No AI tags available.</em>')
        return format_html(
            "<b>AI Tags:</b> {}",
            obj.ai_tags
        )
    ai_metadata_preview.short_description = 'AI Metadata Preview'

    def preview_link(self, obj):
        if obj.file:
            return format_html(f"<a href='{obj.file.url}' target='_blank'>View</a>")
        return "-"
    preview_link.short_description = "Preview"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'institution'):
            return qs.filter(institution=request.user.institution)
        return qs.none()
