from django.contrib import admin
from .models import (
    Supplier, ProcurementRequest, Tender, Quotation,
    PurchaseOrder, GoodsReceivedNote, SupplierInvoice,
    Payment, ProcurementApproval, ProcurementLog
)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'tax_id', 'rating', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone', 'tax_id')
    list_filter = ('is_active', 'created_at')


@admin.register(ProcurementRequest)
class ProcurementRequestAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'requested_by', 'department', 'quantity', 'status', 'required_by', 'created_at')
    search_fields = ('item_name', 'requested_by__username', 'department')
    list_filter = ('status', 'category', 'created_at')
    raw_id_fields = ('requested_by',)


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ('title', 'request', 'published_date', 'closing_date', 'is_closed')
    search_fields = ('title',)
    list_filter = ('is_closed', 'published_date', 'closing_date')


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'request', 'price_per_unit', 'delivery_time_days', 'submitted_at', 'is_selected')
    search_fields = ('supplier__name', 'request__item_name')
    list_filter = ('is_selected', 'submitted_at')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'request', 'supplier', 'quotation', 'total_price', 'issue_date', 'expected_delivery_date')
    search_fields = ('po_number', 'supplier__name')
    list_filter = ('issue_date', 'expected_delivery_date')
    raw_id_fields = ('issued_by',)


@admin.register(GoodsReceivedNote)
class GoodsReceivedNoteAdmin(admin.ModelAdmin):
    list_display = ('po', 'received_by', 'received_date', 'quantity_received')
    search_fields = ('po__po_number', 'received_by__username')
    list_filter = ('received_date',)


@admin.register(SupplierInvoice)
class SupplierInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'po', 'amount', 'invoice_date', 'due_date', 'is_paid')
    search_fields = ('invoice_number', 'po__po_number')
    list_filter = ('is_paid', 'invoice_date', 'due_date')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'paid_on', 'amount', 'method', 'reference')
    search_fields = ('invoice__invoice_number', 'reference')
    list_filter = ('method', 'paid_on')


@admin.register(ProcurementApproval)
class ProcurementApprovalAdmin(admin.ModelAdmin):
    list_display = ('request', 'approved_by', 'primary_role', 'approved_on', 'status')
    search_fields = ('approved_by__username', 'primary_role')
    list_filter = ('status', 'approved_on')


@admin.register(ProcurementLog)
class ProcurementLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'timestamp', 'related_request')
    search_fields = ('actor__username', 'action')
    list_filter = ('timestamp',)
    raw_id_fields = ('actor', 'related_request')
