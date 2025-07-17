import django_filters
from django_filters import rest_framework as filters
from .models import (
    Income, Expense, Refund, Waiver, Budget, WalletTransaction,
    StudentFinanceSnapshot, AnomalyFlag, ScholarshipCandidate,
    StudentInvoice, TransactionLog, ApprovalRequest,
    RecurringTransaction, JournalEntry, AuditTrail, FinanceNotification
)
from academics.models import AcademicYear, Term
from students.models import Student
from institutions.models import Institution
from django.contrib.auth import get_user_model

User = get_user_model()


class IncomeFilter(filters.FilterSet):
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr="lte")
    date_range = filters.DateFromToRangeFilter(field_name="received_on")
    source_name = filters.CharFilter(field_name="source__name", lookup_expr="icontains")
    currency_code = filters.CharFilter(field_name="currency__code", lookup_expr="iexact")
    institution = filters.ModelChoiceFilter(field_name="budget__institution", queryset=Institution.objects.all())

    class Meta:
        model = Income
        fields = ['currency_code', 'source_name', 'date_range', 'institution']


class ExpenseFilter(filters.FilterSet):
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr="lte")
    date_range = filters.DateFromToRangeFilter(field_name="spent_on")
    category_name = filters.CharFilter(field_name="category__name", lookup_expr="icontains")
    currency_code = filters.CharFilter(field_name="currency__code", lookup_expr="iexact")
    institution = filters.ModelChoiceFilter(field_name="budget__institution", queryset=Institution.objects.all())

    class Meta:
        model = Expense
        fields = ['currency_code', 'category_name', 'date_range', 'institution']


class BudgetFilter(filters.FilterSet):
    class Meta:
        model = Budget
        fields = ['institution', 'academic_year', 'term']


class RefundFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Refund._meta.get_field('status').choices)
    student = filters.ModelChoiceFilter(queryset=Student.objects.all())
    date_range = filters.DateFromToRangeFilter(field_name="requested_on")

    class Meta:
        model = Refund
        fields = ['status', 'student', 'date_range']


class WaiverFilter(filters.FilterSet):
    student = filters.ModelChoiceFilter(queryset=Student.objects.all())

    class Meta:
        model = Waiver
        fields = ['student', 'term', 'academic_year']


class WalletTransactionFilter(filters.FilterSet):
    type = filters.ChoiceFilter(choices=WalletTransaction._meta.get_field('type').choices)
    date_range = filters.DateFromToRangeFilter(field_name="created_at")
    student = filters.ModelChoiceFilter(field_name="wallet__student", queryset=Student.objects.all())

    class Meta:
        model = WalletTransaction
        fields = ['type', 'date_range', 'student']


class StudentFinanceSnapshotFilter(filters.FilterSet):
    min_balance = filters.NumberFilter(field_name="balance", lookup_expr="gte")
    max_balance = filters.NumberFilter(field_name="balance", lookup_expr="lte")

    class Meta:
        model = StudentFinanceSnapshot
        fields = ['student', 'academic_year', 'term', 'min_balance', 'max_balance']


class AnomalyFlagFilter(filters.FilterSet):
    resolved = filters.BooleanFilter()
    date_range = filters.DateFromToRangeFilter(field_name="flagged_on")
    student = filters.ModelChoiceFilter(queryset=Student.objects.all())

    class Meta:
        model = AnomalyFlag
        fields = ['resolved', 'date_range', 'student']


class ScholarshipCandidateFilter(filters.FilterSet):
    min_score = filters.NumberFilter(field_name='score', lookup_expr='gte')
    max_score = filters.NumberFilter(field_name='score', lookup_expr='lte')
    min_need_score = filters.NumberFilter(field_name='need_score', lookup_expr='gte')
    max_need_score = filters.NumberFilter(field_name='need_score', lookup_expr='lte')

    class Meta:
        model = ScholarshipCandidate
        fields = ['academic_year', 'recommended_by_ai', 'student', 'min_score', 'max_score', 'min_need_score', 'max_need_score']


class StudentInvoiceFilter(filters.FilterSet):
    due_before = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    due_after = filters.DateFilter(field_name='due_date', lookup_expr='gte')
    status = filters.CharFilter(lookup_expr='iexact')
    invoice_number = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = StudentInvoice
        fields = ['student', 'academic_year', 'term', 'status', 'due_before', 'due_after', 'invoice_number']


class TransactionLogFilter(filters.FilterSet):
    date_range = filters.DateFromToRangeFilter(field_name='timestamp')
    actor = filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = TransactionLog
        fields = ['action', 'actor', 'date_range']


class ApprovalRequestFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=ApprovalRequest._meta.get_field('status').choices)
    date_range = filters.DateFromToRangeFilter(field_name='requested_on')

    class Meta:
        model = ApprovalRequest
        fields = ['request_type', 'status', 'requested_by', 'approved_by', 'date_range']


class RecurringTransactionFilter(filters.FilterSet):
    type = filters.ChoiceFilter(choices=RecurringTransaction._meta.get_field('type').choices)
    frequency = filters.ChoiceFilter(choices=RecurringTransaction._meta.get_field('frequency').choices)
    next_run_range = filters.DateFromToRangeFilter(field_name='next_run')

    class Meta:
        model = RecurringTransaction
        fields = ['type', 'frequency', 'active', 'next_run_range']


class JournalEntryFilter(filters.FilterSet):
    date_range = filters.DateFromToRangeFilter(field_name='date')
    posted_by = filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = JournalEntry
        fields = ['debit_account', 'credit_account', 'posted_by', 'date_range']


class AuditTrailFilter(filters.FilterSet):
    date_range = filters.DateFromToRangeFilter(field_name='timestamp')

    class Meta:
        model = AuditTrail
        fields = ['model_name', 'action', 'performed_by', 'date_range']


class FinanceNotificationFilter(filters.FilterSet):
    date_range = filters.DateFromToRangeFilter(field_name='created_at')

    class Meta:
        model = FinanceNotification
        fields = ['recipient', 'read', 'date_range']
