from django.contrib import admin
from import_export.admin import ExportMixin
from import_export import resources
from .models import Institution, SchoolAccount

# ============================
# Import/Export Resources
# ============================

class InstitutionResource(resources.ModelResource):
    class Meta:
        model = Institution
        fields = '__all__'

class SchoolAccountResource(resources.ModelResource):
    class Meta:
        model = SchoolAccount
        fields = '__all__'

# ============================
# Institution Admin
# ============================

@admin.register(Institution)
class InstitutionAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = InstitutionResource
    list_display = (
        'name', 'code', 'school_type', 'category',
        'county', 'sub_county', 'ward', 'created_at'
    )
    search_fields = ('name', 'code', 'county', 'sub_county', 'ward')
    list_filter = ('school_type', 'county', 'sub_county')
    readonly_fields = ('code', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'code', 'school_type')
        }),
        ('Location', {
            'fields': ('county', 'sub_county', 'ward')
        }),
        ('Branding & Contact', {
            'fields': ('logo', 'theme_color', 'email', 'phone_number', 'website')
        }),
        ('Audit Info', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    @admin.display(description='Category')
    def category(self, obj):
        # Example logic: title case the school_type for display
        return obj.school_type.title()

# ============================
# School Account Admin
# ============================

@admin.register(SchoolAccount)
class SchoolAccountAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = SchoolAccountResource
    list_display = (
        'institution', 'account_name', 'account_number',
        'bank_name', 'payment_type', 'is_default'
    )
    search_fields = ('account_name', 'account_number', 'bank_name')
    list_filter = ('payment_type', 'is_default')
    ordering = ('institution', 'account_name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': (
                'institution', 'account_name', 'account_number',
                'bank_name', 'branch', 'payment_type', 'is_default'
            )
        }),
        ('Audit Info', {
            'fields': ('created_at', 'updated_at')
        }),
    )
