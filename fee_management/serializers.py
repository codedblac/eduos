from rest_framework import serializers
from .models import (
    FeeItem, FeeStructure, FeeStructureItem, Invoice, InvoiceItem,
    Payment, Receipt, Penalty, BursaryAllocation, RefundRequest
)
from students.models import Student
from accounts.models import CustomUser


class FeeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeItem
        fields = '__all__'


class FeeStructureItemSerializer(serializers.ModelSerializer):
    fee_item = FeeItemSerializer(read_only=True)

    class Meta:
        model = FeeStructureItem
        fields = '__all__'


class FeeStructureSerializer(serializers.ModelSerializer):
    items = FeeItemSerializer(many=True, read_only=True)

    class Meta:
        model = FeeStructure
        fields = '__all__'


class InvoiceItemSerializer(serializers.ModelSerializer):
    fee_item_detail = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceItem
        fields = '__all__'

    def get_fee_item_detail(self, obj):
        return FeeItemSerializer(obj.fee_item).data


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(source='items', many=True, read_only=True)
    student_name = serializers.SerializerMethodField()
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'

    def get_student_name(self, obj):
        return str(obj.student)


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    invoice_reference = serializers.SerializerMethodField()
    received_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

    def get_student_name(self, obj):
        return str(obj.student)

    def get_invoice_reference(self, obj):
        return f"INV-{obj.invoice.id}" if obj.invoice else None

    def get_received_by_name(self, obj):
        return str(obj.received_by) if obj.received_by else None


class ReceiptSerializer(serializers.ModelSerializer):
    payment_detail = PaymentSerializer(read_only=True)
    issued_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Receipt
        fields = '__all__'

    def get_issued_by_name(self, obj):
        return str(obj.issued_by) if obj.issued_by else None


class PenaltySerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Penalty
        fields = '__all__'

    def get_student_name(self, obj):
        return str(obj.student)


class BursaryAllocationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    invoice_item_detail = InvoiceItemSerializer(source='invoice_item', read_only=True)

    class Meta:
        model = BursaryAllocation
        fields = '__all__'

    def get_student_name(self, obj):
        return str(obj.student)


class RefundRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    requested_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RefundRequest
        fields = '__all__'

    def get_student_name(self, obj):
        return str(obj.student)

    def get_requested_by_name(self, obj):
        return str(obj.requested_by) if obj.requested_by else None

    def get_approved_by_name(self, obj):
        return str(obj.approved_by) if obj.approved_by else None
