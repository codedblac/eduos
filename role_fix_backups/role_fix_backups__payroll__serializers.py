from rest_framework import serializers
from .models import (
    PayrollProfile, Allowance, Deduction, PayrollRun,
    Payslip, SalaryAdvanceRequest, BankAccount, PayrollAuditLog
)
from staff.models import StaffProfile
from staff.serializers import StaffProfileSerializer


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'id', 'staff_profile', 'bank_name', 'account_number',
            'account_name', 'branch', 'is_primary'
        ]


class AllowanceSerializer(serializers.ModelSerializer):
    staff_profile = StaffProfileSerializer(read_only=True)
    staff_profile_id = serializers.PrimaryKeyRelatedField(
        queryset=StaffProfile.objects.all(),
        source='staff_profile',
        write_only=True
    )

    class Meta:
        model = Allowance
        fields = [
            'id', 'name', 'amount', 'staff_profile', 'staff_profile_id',
            'is_taxable', 'notes'
        ]


class DeductionSerializer(serializers.ModelSerializer):
    staff_profile = StaffProfileSerializer(read_only=True)
    staff_profile_id = serializers.PrimaryKeyRelatedField(
        queryset=StaffProfile.objects.all(),
        source='staff_profile',
        write_only=True
    )
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Deduction
        fields = [
            'id', 'staff_profile', 'staff_profile_id', 'type', 'amount',
            'reason', 'created_by_name', 'created_at'
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class PayrollProfileSerializer(serializers.ModelSerializer):
    staff_profile = StaffProfileSerializer(read_only=True)
    staff_profile_id = serializers.PrimaryKeyRelatedField(
        queryset=StaffProfile.objects.all(), source='staff_profile', write_only=True
    )
    bank_account = BankAccountSerializer(read_only=True)
    bank_account_id = serializers.PrimaryKeyRelatedField(
        queryset=BankAccount.objects.all(), source='bank_account', write_only=True, required=False
    )

    class Meta:
        model = PayrollProfile
        fields = [
            'id', 'staff_profile', 'staff_profile_id',
            'basic_salary', 'benefits', 'tax_identifier',
            'bank_account', 'bank_account_id', 'is_active', 'created_at'
        ]


class PayrollRunSerializer(serializers.ModelSerializer):
    processed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PayrollRun
        fields = [
            'id', 'institution', 'period_start', 'period_end',
            'processed_on', 'processed_by', 'processed_by_name',
            'is_locked', 'notes'
        ]

    def get_processed_by_name(self, obj):
        return obj.processed_by.get_full_name() if obj.processed_by else None


class PayslipSerializer(serializers.ModelSerializer):
    staff_profile = StaffProfileSerializer(read_only=True)
    payroll_run = PayrollRunSerializer(read_only=True)

    class Meta:
        model = Payslip
        fields = [
            'id', 'staff_profile', 'payroll_run',
            'gross_salary', 'total_allowances', 'total_deductions',
            'net_pay', 'pdf_file', 'generated_on'
        ]


class SalaryAdvanceRequestSerializer(serializers.ModelSerializer):
    staff_profile = StaffProfileSerializer(read_only=True)
    staff_profile_id = serializers.PrimaryKeyRelatedField(
        queryset=StaffProfile.objects.all(), source='staff_profile', write_only=True
    )
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SalaryAdvanceRequest
        fields = [
            'id', 'staff_profile', 'staff_profile_id',
            'amount', 'reason', 'requested_on', 'status',
            'reviewed_by_name', 'reviewed_on'
        ]

    def get_reviewed_by_name(self, obj):
        return obj.reviewed_by.get_full_name() if obj.reviewed_by else None


class PayrollAuditLogSerializer(serializers.ModelSerializer):
    staff_profile = StaffProfileSerializer(read_only=True)
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PayrollAuditLog
        fields = [
            'id', 'staff_profile', 'action',
            'performed_by_name', 'changes', 'timestamp'
        ]

    def get_performed_by_name(self, obj):
        return obj.performed_by.get_full_name() if obj.performed_by else None
