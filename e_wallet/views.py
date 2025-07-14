from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from e_wallet.models import (
    Wallet,
    WalletTransaction,
    MicroFee,
    MicroFeePayment,
    WalletTopUpRequest,
    WalletPolicy,
)
from e_wallet.serializers import (
    WalletTransactionSerializer,
    WalletPolicySerializer,
    WalletTopUpRequestSerializer,
    WalletTransactionSerializer,
    WalletPolicySerializer,
    MicroFeeSerializer,
    MicroFeeAssignmentSerializer,
    StudentWalletSerializer,
)
from e_wallet.permissions import (
    IsParent,
    IsStudent,
    IsTeacher,
    IsAdminOrFinance,
    IsOwnerOrReadOnly,
    CanInitiateMicroFees
)
from e_wallet.filters import (
    WalletTransactionFilter,
    MicroFeeFilter,
    WalletFilter
)


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.select_related('student', 'institution')
    serializer_class = StudentWalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = WalletFilter
    ordering_fields = ['balance', 'last_updated']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Wallet.objects.filter(student__user=user)
        if user.role == 'parent':
            return Wallet.objects.filter(student__guardians=user)
        return super().get_queryset()


class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WalletTransaction.objects.select_related('wallet', 'wallet__student')
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = WalletTransactionFilter
    ordering_fields = ['amount', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return WalletTransaction.objects.filter(wallet__student__user=user)
        if user.role == 'parent':
            return WalletTransaction.objects.filter(wallet__student__guardians=user)
        return super().get_queryset()


class MicroFeeViewSet(viewsets.ModelViewSet):
    queryset = MicroFee.objects.prefetch_related('students').select_related('teacher')
    serializer_class = MicroFeeSerializer
    permission_classes = [permissions.IsAuthenticated, CanInitiateMicroFees]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MicroFeeFilter
    search_fields = ['title', 'description']
    ordering_fields = ['amount', 'due_date', 'created_at']

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def payments(self, request, pk=None):
        fee = self.get_object()
        payments = MicroFeePayment.objects.filter(micro_fee=fee)
        serializer = MicroFeeAssignmentSerializer(payments, many=True)
        return Response(serializer.data)


class MicroFeePaymentViewSet(viewsets.ModelViewSet):
    queryset = MicroFeePayment.objects.select_related('micro_fee', 'student')
    serializer_class = MicroFeeAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return MicroFeePayment.objects.filter(student__user=user)
        if user.role == 'parent':
            return MicroFeePayment.objects.filter(student__guardians=user)
        return super().get_queryset()


class WalletTopUpRequestViewSet(viewsets.ModelViewSet):
    queryset = WalletTopUpRequest.objects.select_related('student', 'parent')
    serializer_class = WalletTopUpRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsParent]

    def get_queryset(self):
        return WalletTopUpRequest.objects.filter(parent=self.request.user)

    def perform_create(self, serializer):
        serializer.save(parent=self.request.user)


class WalletPolicyViewSet(viewsets.ModelViewSet):
    queryset = WalletPolicy.objects.select_related('institution')
    serializer_class = WalletPolicySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrFinance]
