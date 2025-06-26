from django.contrib import admin
from .models import (
    IDCardTemplate, IDCard, IDCardAuditLog,
    IDCardReissueRequest, DigitalIDToken
)


@admin.register(IDCardTemplate)
class IDCardTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'font', 'include_qr_code', 'include_barcode', 'active', 'created_at')
    list_filter = ('institution', 'active', 'include_qr_code', 'include_barcode')
    search_fields = ('name', 'institution__name')


@admin.register(IDCard)
class IDCardAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'role', 'institution', 'unique_id', 'issued_on', 'expiry_date',
        'is_active', 'revoked', 'printed'
    )
    list_filter = ('role', 'institution', 'is_active', 'revoked', 'printed', 'digital_only')
    search_fields = ('full_name', 'unique_id', 'class_or_department')
    readonly_fields = ('qr_code_image', 'barcode_image', 'last_printed_on')
    autocomplete_fields = ('user', 'template')  # Removed 'content_type'
    date_hierarchy = 'issued_on'
    fieldsets = (
        ('Basic Info', {
            'fields': ('full_name', 'photo', 'role', 'institution', 'user', 'template')  # Removed content_type & object_id
        }),
        ('Details', {
            'fields': (
                'unique_id', 'class_or_department', 'issued_on', 'expiry_date', 'is_active',
                'revoked', 'reason_revoked', 'digital_only', 'printed', 'last_printed_on'
            )
        }),
        ('Media', {
            'fields': ('qr_code_image', 'barcode_image')
        }),
    )


@admin.register(IDCardAuditLog)
class IDCardAuditLogAdmin(admin.ModelAdmin):
    list_display = ('id_card', 'action', 'performed_by', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('id_card__full_name', 'performed_by__username')
    autocomplete_fields = ('id_card', 'performed_by')


@admin.register(IDCardReissueRequest)
class IDCardReissueRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'approved', 'handled_by', 'created_on', 'approved_on')
    list_filter = ('approved', 'created_on')
    search_fields = ('requester__username', 'handled_by__username')
    autocomplete_fields = ('requester', 'handled_by')
    readonly_fields = ('created_on',)


@admin.register(DigitalIDToken)
class DigitalIDTokenAdmin(admin.ModelAdmin):
    list_display = ('id_card', 'token', 'valid_until', 'created_at')
    search_fields = ('id_card__full_name', 'token')
    readonly_fields = ('created_at',)
