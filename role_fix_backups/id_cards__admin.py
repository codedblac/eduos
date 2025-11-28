from django.contrib import admin
from .models import (
    IDCardTemplate,
    IDCard,
    IDCardAuditLog,
    IDCardReissueRequest,
    DigitalIDToken
)


@admin.register(IDCardTemplate)
class IDCardTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'active', 'created_at')
    list_filter = ('institution', 'active')
    search_fields = ('name', 'institution__name')


@admin.register(IDCard)
class IDCardAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'primary_role', 'unique_id', 'institution', 'status', 'issued_on', 'printed')
    list_filter = ('primary_role', 'status', 'institution', 'printed')
    search_fields = ('full_name', 'unique_id', 'class_or_department')
    readonly_fields = ('qr_code_image', 'barcode_image', 'created_at')


@admin.register(IDCardAuditLog)
class IDCardAuditLogAdmin(admin.ModelAdmin):
    list_display = ('id_card', 'action', 'performed_by', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('id_card__full_name', 'performed_by__username')


@admin.register(IDCardReissueRequest)
class IDCardReissueRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'reason', 'approved', 'handled_by', 'approved_on', 'created_on')
    list_filter = ('approved', 'approved_on')
    search_fields = ('requester__username', 'reason')


@admin.register(DigitalIDToken)
class DigitalIDTokenAdmin(admin.ModelAdmin):
    list_display = ('id_card', 'token', 'valid_until', 'created_at')
    search_fields = ('id_card__full_name', 'token')
    readonly_fields = ('created_at',)
