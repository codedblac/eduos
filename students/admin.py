from django.contrib import admin
from .models import Student, MedicalFlag, StudentHistory

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'admission_number', 'institution', 'class_level', 'stream', 'enrollment_status', 'date_joined'
    ]
    list_filter = ['institution', 'class_level', 'stream', 'enrollment_status']
    search_fields = ['first_name', 'last_name', 'admission_number', 'national_id']
    ordering = ['class_level', 'stream', 'last_name', 'first_name']
    autocomplete_fields = ['institution', 'class_level', 'stream', 'assigned_class_teacher']

    def full_name(self, obj):
        # Handles middle name gracefully if present
        if obj.middle_name:
            return f"{obj.first_name} {obj.middle_name} {obj.last_name}"
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'


@admin.register(MedicalFlag)
class MedicalFlagAdmin(admin.ModelAdmin):
    list_display = ['student', 'condition', 'critical', 'created_at']
    list_filter = ['critical', 'condition']
    search_fields = ['student__first_name', 'student__last_name', 'condition']
    ordering = ['-created_at']
    autocomplete_fields = ['student']


@admin.register(StudentHistory)
class StudentHistoryAdmin(admin.ModelAdmin):
    list_display = ['student', 'change_type', 'old_class', 'new_class', 'old_stream', 'new_stream', 'date_changed', 'changed_by']
    list_filter = ['change_type', 'old_class', 'new_class', 'old_stream', 'new_stream']
    search_fields = ['student__first_name', 'student__last_name', 'change_type', 'changed_by__username']
    ordering = ['-date_changed']
    autocomplete_fields = ['student', 'old_class', 'new_class', 'old_stream', 'new_stream', 'changed_by']
