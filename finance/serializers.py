# finance/serializers.py

from rest_framework import serializers
from .models import (
    Currency, FundSource, Budget, Income, Expense,
    Refund, Waiver, StudentWallet, WalletTransaction,
    StudentFinanceSnapshot, TransactionLog, ApprovalRequest,
    FinanceNotification, AnomalyFlag, ScholarshipCandidate,
    StudentInvoice
)
from students.models import Student
from academics.models import AcademicYear, Term
from institutions.models import Institution


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class FundSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundSource
        fields = '__all__'


class BudgetSerializer(serializers.ModelSerializer):
    institution_name = serializers.StringRelatedField(source='institution', read_only=True)
    term_display = serializers.StringRelatedField(source='term', read_only=True)
    year_display = serializers.StringRelatedField(source='academic_year', read_only=True)
    created_by_name = serializers.StringRelatedField(source='created_by', read_only=True)

    class Meta:
        model = Budget
        fields = '__all__'


class IncomeSerializer(serializers.ModelSerializer):
    source_name = serializers.StringRelatedField(source='source', read_only=True)
    currency_code = serializers.StringRelatedField(source='currency', read_only=True)
    received_by_name = serializers.StringRelatedField(source='received_by', read_only=True)

    class Meta:
        model = Income
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    currency_code = serializers.StringRelatedField(source='currency', read_only=True)
    spent_by_name = serializers.StringRelatedField(source='spent_by', read_only=True)

    class Meta:
        model = Expense
        fields = '__all__'


class RefundSerializer(serializers.ModelSerializer):
    student_name = serializers.StringRelatedField(source='student', read_only=True)
    approved_by_name = serializers.StringRelatedField(source='approved_by', read_only=True)

    class Meta:
        model = Refund
        fields = '__all__'


class WaiverSerializer(serializers.ModelSerializer):
    student_name = serializers.StringRelatedField(source='student', read_only=True)
    approved_by_name = serializers.StringRelatedField(source='approved_by', read_only=True)
    term_name = serializers.StringRelatedField(source='term', read_only=True)
    year_name = serializers.StringRelatedField(source='academic_year', read_only=True)

    class Meta:
        model = Waiver
        fields = '__all__'


class StudentWalletSerializer(serializers.ModelSerializer):
    student_name = serializers.StringRelatedField(source='student', read_only=True)

    class Meta:
        model = StudentWallet
        fields = '__all__'


class WalletTransactionSerializer(serializers.ModelSerializer):
    wallet_student_name = serializers.StringRelatedField(source='wallet.student', read_only=True)

    class Meta:
        model = WalletTransaction
        fields = '__all__'


class StudentFinanceSnapshotSerializer(serializers.ModelSerializer):
    student_name = serializers.StringRelatedField(source='student', read_only=True)
    term_name = serializers.StringRelatedField(source='term', read_only=True)
    academic_year_name = serializers.StringRelatedField(source='academic_year', read_only=True)

    class Meta:
        model = StudentFinanceSnapshot
        fields = '__all__'


class TransactionLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.StringRelatedField(source='actor', read_only=True)

    class Meta:
        model = TransactionLog
        fields = '__all__'


class ApprovalRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.StringRelatedField(source='requested_by', read_only=True)
    approved_by_name = serializers.StringRelatedField(source='approved_by', read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = '__all__'


class FinanceNotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.StringRelatedField(source='recipient', read_only=True)

    class Meta:
        model = FinanceNotification
        fields = '__all__'


class AnomalyFlagSerializer(serializers.ModelSerializer):
    student_name = serializers.StringRelatedField(source='student', read_only=True)

    class Meta:
        model = AnomalyFlag
        fields = '__all__'


class ScholarshipCandidateSerializer(serializers.ModelSerializer):
    student_name = serializers.StringRelatedField(source='student', read_only=True)
    academic_year_display = serializers.StringRelatedField(source='academic_year', read_only=True)

    class Meta:
        model = ScholarshipCandidate
        fields = '__all__'


class StudentInvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.StringRelatedField(source='student', read_only=True)
    academic_year_name = serializers.StringRelatedField(source='academic_year', read_only=True)
    term_name = serializers.StringRelatedField(source='term', read_only=True)
    created_by_name = serializers.StringRelatedField(source='created_by', read_only=True)

    class Meta:
        model = StudentInvoice
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'status', 'balance', 'created_by']
