from django.contrib import admin
from .models import ClassLevel, Stream

@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'institution', 'order', 'created_at')
    list_filter = ('institution',)
    search_fields = ('name', 'code', 'institution__name')
    ordering = ('institution', 'order', 'name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('institution', 'name', 'code', 'order', 'description')
        }),
        ('Audit Info', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'class_level', 'order', 'created_at')  # Removed 'timetable'
    list_filter = ('class_level__institution', 'class_level')
    search_fields = ('name', 'code', 'class_level__name')
    ordering = ('class_level', 'order', 'name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('class_level', 'name', 'code', 'order', 'description')  # Removed 'timetable'
        }),
        ('Audit Info', {
            'fields': ('created_at', 'updated_at')
        }),
    )
