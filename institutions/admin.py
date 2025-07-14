from django.contrib import admin
from .models import Institution, SchoolAccount


@admin.register(SchoolAccount)
class SchoolAccountAdmin(admin.ModelAdmin):
    list_display = (
        'institution', 'account_name', 'account_number', 'payment_type',
        'bank_name', 'mpesa_till_number', 'is_default',
        'created_at', 'updated_at',
    )
    list_filter = ('payment_type', 'is_default', 'institution__county', 'institution__school_type')
    search_fields = ('account_name', 'account_number', 'bank_name', 'institution__name')
    ordering = ('-created_at',)
    autocomplete_fields = ('institution',)
    readonly_fields = ('created_at', 'updated_at')


class SchoolAccountInline(admin.TabularInline):
    model = SchoolAccount
    extra = 1
    fields = ('account_name', 'account_number', 'payment_type', 'is_default')
    show_change_link = True


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'code', 'institution_type', 'school_type',
        'country', 'county', 'sub_county', 'ward',
        'phone', 'email', 'established_year', 'created_at',
    )
    list_filter = ('institution_type', 'school_type', 'country', 'county')
    search_fields = ('name', 'code', 'email', 'phone', 'registration_number')
    ordering = ('name',)
    inlines = [SchoolAccountInline]

    fieldsets = (
        ("Basic Information", {
            'fields': ('name', 'code', 'registration_number', 'institution_type', 'school_type')
        }),
        ("Location & Contact", {
            'fields': ('country', 'county', 'sub_county', 'ward', 'village', 'address', 'phone', 'email', 'website')
        }),
        ("Branding", {
            'fields': ('logo', 'primary_color', 'secondary_color', 'theme_mode')
        }),
        ("Ownership & Establishment", {
            'fields': ('ownership', 'funding_source', 'established_year')
        }),
        ("Timestamps & Metadata", {
            'fields': ('created_at', 'updated_at', 'extra_info')
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
