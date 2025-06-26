from django.contrib import admin
from import_export.admin import ExportMixin
from .models import (
    MedicineInventory, MedicalVisit, SickBayVisit,
    DispensedMedicine, MedicalFlag, HealthAlert, ClassHealthTrend
)


@admin.register(MedicineInventory)
class MedicineInventoryAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'institution', 'quantity', 'unit', 'expiry_date', 'restock_level', 'created_at')
    list_filter = ('institution', 'expiry_date')
    search_fields = ('name',)
    ordering = ('name',)


class DispensedMedicineInline(admin.TabularInline):
    model = DispensedMedicine
    extra = 1


@admin.register(MedicalVisit)
class MedicalVisitAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('student', 'attended_by', 'date_visited', 'diagnosis', 'is_emergency', 'referred')
    list_filter = ('is_emergency', 'referred', 'date_visited')
    search_fields = ('student__user__username', 'attended_by__username', 'diagnosis')
    autocomplete_fields = ('student', 'attended_by')
    inlines = [DispensedMedicineInline]
    date_hierarchy = 'date_visited'
    ordering = ('-date_visited',)


@admin.register(SickBayVisit)
class SickBayVisitAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('student', 'institution', 'visit_date', 'diagnosis')
    list_filter = ('institution', 'visit_date')
    search_fields = ('student__user__username', 'diagnosis')
    autocomplete_fields = ('student', 'institution')
    date_hierarchy = 'visit_date'
    ordering = ('-visit_date',)


@admin.register(MedicalFlag)
class MedicalFlagAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('student', 'flag_type', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('student__user__username', 'flag_type')
    autocomplete_fields = ('student',)
    ordering = ('-created_at',)


@admin.register(HealthAlert)
class HealthAlertAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('student', 'alert_type', 'triggered_by_ai', 'resolved', 'date_created')
    list_filter = ('triggered_by_ai', 'resolved', 'date_created')
    search_fields = ('student__user__username', 'alert_type')
    autocomplete_fields = ('student',)
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)


@admin.register(ClassHealthTrend)
class ClassHealthTrendAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('institution', 'class_level', 'stream_name', 'most_common_illness', 'generated_on')
    list_filter = ('institution', 'class_level', 'generated_on')
    search_fields = ('class_level', 'stream_name', 'most_common_illness')
    autocomplete_fields = ('institution',)
    date_hierarchy = 'generated_on'
    ordering = ('-generated_on',)


@admin.register(DispensedMedicine)
class DispensedMedicineAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('visit', 'medicine', 'quantity_dispensed')
    list_filter = ('medicine',)
    search_fields = ('visit__student__user__username', 'medicine__name')
    autocomplete_fields = ('visit', 'medicine')
