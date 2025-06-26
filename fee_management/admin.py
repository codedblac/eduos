from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from django.http import HttpResponse
from django.db.models import Sum
import csv

from .models import (
    FeeItem, FeeStructure, FeeStructureItem, Invoice, InvoiceItem,
    Payment, Receipt, Penalty, BursaryAllocation, RefundRequest
)

# ------------------------------
# Admin Utilities
# ------------------------------

def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)
    fields = [field.name for field in modeladmin.model._meta.fields]
    writer.writerow(fields)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])
    return response

export_as_csv.short_description = "Export selected to CSV"


class UnpaidInvoiceFilter(admin.SimpleListFilter):
    title = 'Payment Status'
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        return (
            ('unpaid', 'Unpaid'),
            ('overdue', 'Overdue'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'unpaid':
            return queryset.filter(is_paid=False, status__in=['issued', 'overdue'])
        if self.value() == 'overdue':
            return queryset.filter(status='overdue', is_paid=False)
        return queryset


# ------------------------------
# Fee Admins
# ------------------------------

@admin.register(FeeItem)
class FeeItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'class_level', 'term', 'is_mandatory', 'active')
    list_filter = ('class_level', 'term', 'is_mandatory', 'active')
    search_fields = ('name', 'description')


class FeeStructureItemInline(admin.TabularInline):
    model = FeeStructureItem
    extra = 0


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'stream', 'term', 'year', 'total_amount', 'institution')
    list_filter = ('class_level', 'term', 'year')
    inlines = [FeeStructureItemInline]


# ------------------------------
# Invoice Admin
# ------------------------------

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'student', 'total_amount', 'balance_due', 'status', 'is_paid', 'due_date')
    list_filter = ('status', 'term', 'year', UnpaidInvoiceFilter)
    search_fields = ('student__user__username', 'student__admission_number')
    inlines = [InvoiceItemInline]
    actions = [export_as_csv]
    readonly_fields = ('created_at',)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'fee_item', 'amount', 'discount_applied', 'bursary_applied')
    list_filter = ('fee_item',)
    search_fields = ('invoice__student__user__username',)


# ------------------------------
# Payment Admin with Dashboard Metrics
# ------------------------------

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'mode', 'status', 'receipt_number', 'paid_at', 'paid_by', 'received_by')
    list_filter = ('mode', 'status', 'paid_at')
    search_fields = ('student__user__username', 'receipt_number', 'reference_code')
    actions = [export_as_csv]
    readonly_fields = ('created_at', 'updated_at')
    change_list_template = "admin/payments_change_list.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = self.get_queryset(request)
            total_collected = qs.aggregate(total=Sum('amount'))['total'] or 0
            total_today = qs.filter(paid_at__date=now().date()).aggregate(total=Sum('amount'))['total'] or 0
            extra_context = extra_context or {}
            extra_context.update({
                'total_collected': total_collected,
                'total_today': total_today
            })
            response.context_data.update(extra_context)
        except Exception as e:
            self.message_user(request, f"Error generating dashboard: {e}", level='error')
        return response


# ------------------------------
# Receipt Admin with Print PDF
# ------------------------------

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('payment', 'issued_by', 'date_issued', 'print_receipt')
    readonly_fields = ('date_issued',)

    def print_receipt(self, obj):
        if obj.pdf_url:
            return format_html("<a href='{}' target='_blank'>View PDF</a>", obj.pdf_url)
        return "N/A"
    print_receipt.short_description = "Receipt PDF"


# ------------------------------
# Penalty Admin
# ------------------------------

@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'amount', 'waived', 'applied_at')
    list_filter = ('term', 'waived')
    search_fields = ('student__user__username',)


# ------------------------------
# Bursary Allocation Admin
# ------------------------------

@admin.register(BursaryAllocation)
class BursaryAllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'source', 'term', 'year', 'invoice_item')
    search_fields = ('student__user__username', 'source')
    list_filter = ('term', 'year')


# ------------------------------
# Refund Request Admin
# ------------------------------

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'invoice', 'amount', 'status', 'requested_by', 'approved_by', 'refunded_on', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__user__username', 'requested_by__username')
    readonly_fields = ('created_at',)
