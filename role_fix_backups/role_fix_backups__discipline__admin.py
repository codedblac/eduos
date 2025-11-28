from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DisciplineCategory, DisciplineCase, DisciplinaryAction


class DisciplinaryActionInline(admin.TabularInline):
    model = DisciplinaryAction
    extra = 0
    readonly_fields = ['assigned_by', 'date_assigned']
    show_change_link = True


@admin.register(DisciplineCase)
class DisciplineCaseAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'institution', 'category', 'severity',
        'incident_date', 'status', 'reported_by'
    )
    list_filter = (
        'institution', 'category', 'severity', 'status', 'incident_date',
        'class_level', 'stream'
    )
    search_fields = (
        'student__user__first_name', 'student__user__last_name',
        'reported_by__first_name', 'reported_by__last_name',
        'description'
    )
    inlines = [DisciplinaryActionInline]
    readonly_fields = ['created_at', 'reported_by']


@admin.register(DisciplineCategory)
class DisciplineCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution']
    search_fields = ['name']
    list_filter = ['institution']


@admin.register(DisciplinaryAction)
class DisciplinaryActionAdmin(admin.ModelAdmin):
    list_display = ['discipline_case', 'action_taken', 'assigned_by', 'date_assigned']
    search_fields = ['action_taken', 'description']
    list_filter = ['date_assigned', 'follow_up_required']
    readonly_fields = ['assigned_by']
