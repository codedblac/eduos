from rest_framework import serializers
from .models import (
    Supplier, ProcurementRequest, Quotation, PurchaseOrder,
    GoodsReceivedNote, SupplierInvoice, Payment,
    ProcurementApproval, Tender, ProcurementLog
)
from accounts.models import CustomUser
from institutions.models import Institution

# ----------------------------
# Supplier
# ----------------------------
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


# ----------------------------
# Tender
# ----------------------------
class TenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tender
        fields = '__all__'


# ----------------------------
# Procurement Request (Read)
# ----------------------------
class ProcurementRequestReadSerializer(serializers.ModelSerializer):
    requested_by = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    institution = serializers.StringRelatedField()
    approvals = serializers.SerializerMethodField()
    quotations = serializers.SerializerMethodField()

    class Meta:
        model = ProcurementRequest
        fields = '__all__'

    def get_approvals(self, obj):
        approvals = obj.approvals.all()
        return ProcurementApprovalSerializer(approvals, many=True).data

    def get_quotations(self, obj):
        quotations = obj.quotations.all()
        return QuotationSerializer(quotations, many=True).data


# ----------------------------
# Procurement Request (Write)
# ----------------------------
class ProcurementRequestWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcurementRequest
        exclude = ['status']


# ----------------------------
# Quotation
# ----------------------------
class QuotationSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), source='supplier', write_only=True
    )

    class Meta:
        model = Quotation
        fields = [
            'id', 'supplier', 'supplier_id', 'request', 'tender',
            'price_per_unit', 'delivery_time_days', 'notes',
            'attachment', 'submitted_at', 'is_selected'
        ]


# ----------------------------
# Purchase Order
# ----------------------------
class PurchaseOrderSerializer(serializers.ModelSerializer):
    request = ProcurementRequestReadSerializer(read_only=True)
    quotation = QuotationSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    issued_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'


# ----------------------------
# Goods Received Note
# ----------------------------
class GoodsReceivedNoteSerializer(serializers.ModelSerializer):
    po = PurchaseOrderSerializer(read_only=True)
    po_id = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseOrder.objects.all(), source='po', write_only=True
    )
    received_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsReceivedNote
        fields = [
            'id', 'po', 'po_id', 'received_by', 'received_date',
            'quantity_received', 'notes', 'file_upload'
        ]


# ----------------------------
# Supplier Invoice
# ----------------------------
class SupplierInvoiceSerializer(serializers.ModelSerializer):
    po = PurchaseOrderSerializer(read_only=True)
    po_id = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseOrder.objects.all(), source='po', write_only=True
    )

    class Meta:
        model = SupplierInvoice
        fields = [
            'id', 'po', 'po_id', 'invoice_number', 'amount',
            'invoice_date', 'due_date', 'document', 'is_paid'
        ]


# ----------------------------
# Payment
# ----------------------------
class PaymentSerializer(serializers.ModelSerializer):
    invoice = SupplierInvoiceSerializer(read_only=True)
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=SupplierInvoice.objects.all(), source='invoice', write_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_id', 'paid_on',
            'amount', 'method', 'reference'
        ]

    def validate(self, data):
        invoice = data['invoice']
        if invoice.is_paid:
            raise serializers.ValidationError("This invoice is already marked as paid.")
        if data['amount'] > invoice.amount:
            raise serializers.ValidationError("Paid amount exceeds invoice total.")
        return data


# ----------------------------
# Procurement Approval
# ----------------------------
class ProcurementApprovalSerializer(serializers.ModelSerializer):
    approved_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ProcurementApproval
        fields = '__all__'


# ----------------------------
# Procurement Log
# ----------------------------
class ProcurementLogSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ProcurementLog
        fields = '__all__'
