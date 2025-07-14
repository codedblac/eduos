# classes/admin.py

from django.contrib import admin
from .models import ClassLevel, Stream


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'code', 'institution', 'order', 'is_graduating_level',
        'requires_national_exam', 'default_promotion_class', 'created_by', 'updated_by'
    )
    list_filter = ('institution', 'is_graduating_level', 'requires_national_exam')
    search_fields = ('name', 'code', 'institution__name')
    ordering = ('institution__name', 'order', 'name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('institution', 'default_promotion_class', 'created_by', 'updated_by')
    fieldsets = (
        (None, {
            'fields': (
                'institution', 'name', 'code', 'order', 'description',
                'is_graduating_level', 'requires_national_exam', 'default_promotion_class'
            )
        }),
        ('Audit Info', {
            'classes': ('collapse',),
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'code', 'class_level', 'academic_year', 'institution', 'class_teacher',
        'capacity', 'current_student_count', 'is_over_capacity',
        'average_score', 'average_attendance_rate', 'rank_within_class_level',
        'last_ai_evaluation', 'is_active'
    )
    list_filter = (
        'academic_year', 'institution', 'class_level', 'is_active', 'auto_promote_enabled'
    )
    search_fields = (
        'name', 'code', 'class_level__name', 'institution__name', 'academic_year__name',
        'class_teacher__user__first_name', 'class_teacher__user__last_name'
    )
    ordering = ('academic_year', 'class_level__order', 'order')
    readonly_fields = ('created_at', 'updated_at', 'current_student_count', 'is_over_capacity')
    autocomplete_fields = (
        'class_level', 'institution', 'academic_year', 'class_teacher', 'created_by', 'updated_by'
    )
    fieldsets = (
        (None, {
            'fields': (
                'name', 'code', 'order', 'description', 'class_level',
                'academic_year', 'institution', 'class_teacher', 'capacity',
                'is_active', 'auto_promote_enabled'
            )
        }),
        ('Performance & Evaluation', {
            'classes': ('collapse',),
            'fields': (
                'average_score', 'average_attendance_rate', 'rank_within_class_level',
                'last_ai_evaluation'
            )
        }),
        ('Audit Info', {
            'classes': ('collapse',),
            'fields': (
                'created_by', 'updated_by', 'created_at', 'updated_at',
                'current_student_count', 'is_over_capacity'
            )
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('class_level', 'institution', 'academic_year')

