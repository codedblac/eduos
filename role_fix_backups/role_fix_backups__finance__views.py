from rest_framework import viewsets, permissions, filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import *
from .serializers import *
from .filters import *
from .permissions import (
    IsFinanceAdmin, IsAccountant, IsAuditorOrReadOnly,
    IsRefundApprover, IsOwnerOrReadOnly
)

BASE_FILTERS = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.select_related('institution', 'term', 'academic_year', 'created_by')
    serializer_class = BudgetSerializer
    permission_classes = [IsFinanceAdmin | IsAccountant | IsAuditorOrReadOnly]
    filter_backends = BASE_FILTERS
    filterset_class = BudgetFilter
    search_fields = ['institution__name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.select_related('budget', 'source', 'currency', 'received_by')
    serializer_class = IncomeSerializer
    permission_classes = [IsFinanceAdmin | IsAccountant | IsAuditorOrReadOnly]
    filter_backends = BASE_FILTERS
    filterset_class = IncomeFilter
    search_fields = ['description', 'source__name']
    ordering_fields = ['received_on', 'amount']
    ordering = ['-received_on']


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related('budget', 'currency', 'spent_by')
    serializer_class = ExpenseSerializer
    permission_classes = [IsFinanceAdmin | IsAccountant | IsAuditorOrReadOnly]
    filter_backends = BASE_FILTERS
    filterset_class = ExpenseFilter
    search_fields = ['description', 'category__name']
    ordering_fields = ['spent_on', 'amount']
    ordering = ['-spent_on']


class RefundViewSet(viewsets.ModelViewSet):
    queryset = Refund.objects.select_related('student', 'academic_year', 'term', 'approved_by')
    serializer_class = RefundSerializer
    permission_classes = [IsAccountant | IsRefundApprover | IsOwnerOrReadOnly]
    filter_backends = BASE_FILTERS
    filterset_class = RefundFilter
    search_fields = ['student__full_name']
    ordering_fields = ['requested_on', 'amount']
    ordering = ['-requested_on']


class WaiverViewSet(viewsets.ModelViewSet):
    queryset = Waiver.objects.select_related('student', 'term', 'academic_year', 'approved_by')
    serializer_class = WaiverSerializer
    permission_classes = [IsRefundApprover | IsFinanceAdmin]
    filter_backends = BASE_FILTERS
    filterset_class = WaiverFilter
    search_fields = ['student__full_name']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']


class WalletTransactionViewSet(viewsets.ModelViewSet):
    queryset = WalletTransaction.objects.select_related('wallet__student')
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = BASE_FILTERS
    filterset_class = WalletTransactionFilter
    search_fields = ['wallet__student__full_name']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']


class StudentWalletViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentWallet.objects.select_related('student')
    serializer_class = StudentWalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = BASE_FILTERS
    search_fields = ['student__full_name']
    ordering_fields = ['balance']
    ordering = ['-balance']


class StudentFinanceSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentFinanceSnapshot.objects.select_related('student', 'academic_year', 'term')
    serializer_class = StudentFinanceSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = BASE_FILTERS
    filterset_class = StudentFinanceSnapshotFilter
    search_fields = ['student__full_name']
    ordering_fields = ['last_updated', 'balance', 'total_paid', 'total_invoiced']
    ordering = ['-last_updated']


class TransactionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransactionLog.objects.select_related('actor')
    serializer_class = TransactionLogSerializer
    permission_classes = [IsFinanceAdmin | IsAuditorOrReadOnly]
    filter_backends = BASE_FILTERS
    search_fields = ['details', 'actor__full_name']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.select_related('requested_by', 'approved_by')
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsFinanceAdmin | IsRefundApprover]
    filter_backends = BASE_FILTERS
    search_fields = ['request_type', 'requested_by__full_name']
    ordering_fields = ['requested_on', 'status']
    ordering = ['-requested_on']


class FinanceNotificationViewSet(viewsets.ModelViewSet):
    queryset = FinanceNotification.objects.select_related('recipient')
    serializer_class = FinanceNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = BASE_FILTERS
    search_fields = ['recipient__full_name', 'message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class AnomalyFlagViewSet(viewsets.ModelViewSet):
    queryset = AnomalyFlag.objects.select_related('student')
    serializer_class = AnomalyFlagSerializer
    permission_classes = [IsFinanceAdmin | IsAuditorOrReadOnly]
    filter_backends = BASE_FILTERS
    filterset_class = AnomalyFlagFilter
    search_fields = ['student__full_name', 'description']
    ordering_fields = ['flagged_on']
    ordering = ['-flagged_on']


class ScholarshipCandidateViewSet(viewsets.ModelViewSet):
    queryset = ScholarshipCandidate.objects.select_related('student', 'academic_year')
    serializer_class = ScholarshipCandidateSerializer
    permission_classes = [IsFinanceAdmin | IsAuditorOrReadOnly]
    filter_backends = BASE_FILTERS
    filterset_class = ScholarshipCandidateFilter
    search_fields = ['student__full_name']
    ordering_fields = ['score', 'need_score', 'created_at']
    ordering = ['-score']


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = BASE_FILTERS
    search_fields = ['code', 'name']
    ordering_fields = ['code']
    ordering = ['code']


class FundSourceViewSet(viewsets.ModelViewSet):
    queryset = FundSource.objects.all()
    serializer_class = FundSourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = BASE_FILTERS
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']