from django.contrib import admin
from django.utils.html import format_html
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


@admin.register(ELibraryTag)
class ELibraryTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(ResourceVersion)
class ResourceVersionAdmin(admin.ModelAdmin):
    list_display = ('resource', 'uploaded_at', 'file')
    search_fields = ('resource__title',)
    list_filter = ('uploaded_at',)


@admin.register(ResourceViewLog)
class ResourceViewLogAdmin(admin.ModelAdmin):
    list_display = ('resource', 'user', 'viewed_at')
    search_fields = ('resource__title', 'user__username')
    list_filter = ('viewed_at',)


class ELibraryResourceCategoryInline(admin.TabularInline):
    model = ELibraryResource.category.through
    extra = 1


@admin.action(description="Mark selected as Public")
def make_public(modeladmin, request, queryset):
    count = queryset.update(visibility='public')
    modeladmin.message_user(request, f"{count} resource(s) marked as public.")


@admin.action(description="Restrict to Institution Only")
def make_institution_only(modeladmin, request, queryset):
    count = queryset.update(visibility='institution')
    modeladmin.message_user(request, f"{count} resource(s) marked as institution-only.")


@admin.action(description="🧠 Auto-Tag Resources with AI")
def auto_tag_with_ai(modeladmin, request, queryset):
    count = 0
    for resource in queryset:
        tags = ELibraryAIEngine.detect_content_topics(resource)
        if tags:
            resource.ai_tags = ', '.join(tags)
            resource.save(update_fields=['ai_tags'])
            count += 1
    modeladmin.message_user(request, f"{count} resource(s) tagged with AI.")


@admin.action(description="✨ Recommend Resources (Simulated)")
def generate_recommendations(modeladmin, request, queryset):
    recs = ELibraryAIEngine.recommend_resources_for_user(request.user)
    titles = ', '.join([r["title"] for r in recs])
    modeladmin.message_user(request, f"Sample recommendations: {titles}")


@admin.register(ELibraryResource)
class ELibraryResourceAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'uploader', 'institution', 'visibility',
        'file_size', 'file_extension', 'created_at',
        'preview_link', 'ai_metadata_preview',
    )
    list_filter = ('visibility', 'institution', 'category')
    search_fields = ('title', 'description', 'ai_tags')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'ai_metadata_preview', 'preview_link')
    inlines = [ELibraryResourceCategoryInline]
    actions = [make_public, make_institution_only, auto_tag_with_ai, generate_recommendations]
    list_per_page = 30

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'institution', 'visibility', 'uploader')
        }),
        ('File', {
            'fields': ('file', 'external_url', 'file_size', 'file_extension', 'preview_link'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('subject', 'class_level', 'category', 'tags', 'ai_tags', 'ai_metadata_preview'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_approved', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.uploader:
            obj.uploader = request.user
        super().save_model(request, obj, form, change)

    def file_size(self, obj):
        try:
            size = obj.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 ** 2:
                return f"{size / 1024:.1f} KB"
            return f"{size / (1024 ** 2):.1f} MB"
        except Exception:
            return "-"
    file_size.short_description = 'File Size'

    def file_extension(self, obj):
        try:
            return obj.file.name.split('.')[-1].upper()
        except Exception:
            return "-"
    file_extension.short_description = 'Ext'

    def ai_metadata_preview(self, obj):
        return format_html('<span style="color: #555;">{}</span>', obj.ai_tags or "—")
    ai_metadata_preview.short_description = "AI Tags"

    def preview_link(self, obj):
        if obj.file:
            return format_html(f"<a href='{obj.file.url}' target='_blank'>View</a>")
        elif obj.external_url:
            return format_html(f"<a href='{obj.external_url}' target='_blank'>Visit</a>")
        return "-"
    preview_link.short_description = "Preview"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(institution=getattr(request.user, 'institution', None))
