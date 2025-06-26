import django_filters
from django.db.models import Q
from .models import (
    ProcurementRequest, Quotation, PurchaseOrder,
    SupplierInvoice, GoodsReceivedNote, Supplier, Tender
)
from institutions.models import Institution


# ----------------------------
# ProcurementRequest Filter
# ----------------------------
class ProcurementRequestFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    status = django_filters.CharFilter(lookup_expr='icontains')
    item_name = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.CharFilter(lookup_expr='icontains')
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = ProcurementRequest
        fields = [
            'status', 'item_name', 'department', 'institution',
            'created_at__gte', 'created_at__lte'
        ]


# ----------------------------
# PurchaseOrder Filter
# ----------------------------
class PurchaseOrderFilter(django_filters.FilterSet):
    expected_delivery_date__gte = django_filters.DateFilter(field_name='expected_delivery_date', lookup_expr='gte')
    expected_delivery_date__lte = django_filters.DateFilter(field_name='expected_delivery_date', lookup_expr='lte')
    supplier = django_filters.ModelChoiceFilter(queryset=Supplier.objects.all())
    status = django_filters.CharFilter(method='filter_status')

    class Meta:
        model = PurchaseOrder
        fields = [
            'po_number', 'supplier', 'expected_delivery_date__gte',
            'expected_delivery_date__lte', 'status'
        ]

    def filter_status(self, queryset, name, value):
        if value == 'fulfilled':
            return queryset.filter(grn__isnull=False)
        elif value == 'pending':
            return queryset.filter(grn__isnull=True)
        return queryset


# ----------------------------
# SupplierInvoice Filter
# ----------------------------
class SupplierInvoiceFilter(django_filters.FilterSet):
    is_paid = django_filters.BooleanFilter()
    due_date__lt = django_filters.DateFilter(field_name='due_date', lookup_expr='lt')
    due_date__gte = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    po__supplier = django_filters.ModelChoiceFilter(queryset=Supplier.objects.all(), label='Supplier')

    class Meta:
        model = SupplierInvoice
        fields = [
            'is_paid', 'due_date__lt', 'due_date__gte', 'po__supplier'
        ]


# ----------------------------
# GoodsReceivedNote Filter
# ----------------------------
class GoodsReceivedNoteFilter(django_filters.FilterSet):
    received_date__gte = django_filters.DateFilter(field_name='received_date', lookup_expr='gte')
    received_date__lte = django_filters.DateFilter(field_name='received_date', lookup_expr='lte')
    po__supplier = django_filters.ModelChoiceFilter(queryset=Supplier.objects.all())

    class Meta:
        model = GoodsReceivedNote
        fields = [
            'received_date__gte', 'received_date__lte', 'po__supplier'
        ]


# ----------------------------
# Tender Filter
# ----------------------------
class TenderFilter(django_filters.FilterSet):
    closing_date__gte = django_filters.DateFilter(field_name='closing_date', lookup_expr='gte')
    closing_date__lte = django_filters.DateFilter(field_name='closing_date', lookup_expr='lte')
    is_closed = django_filters.BooleanFilter()

    class Meta:
        model = Tender
        fields = ['closing_date__gte', 'closing_date__lte', 'is_closed']
