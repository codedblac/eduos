from django.shortcuts import render
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Q

from rest_framework.views import APIView
from .models import (
    FeeItem, FeeStructure, Invoice, InvoiceItem, Payment,
    Receipt, Penalty, BursaryAllocation, RefundRequest
)
from .serializers import (
    FeeItemSerializer, FeeStructureSerializer, InvoiceSerializer, InvoiceItemSerializer,
    PaymentSerializer, ReceiptSerializer, PenaltySerializer, BursaryAllocationSerializer,
    RefundRequestSerializer
)
from .permissions import IsAdminOrAccountant
from .filters import (
    InvoiceFilter, PaymentFilter, BursaryFilter,
    RefundRequestFilter, PenaltyFilter
)

class FeeItemViewSet(viewsets.ModelViewSet):
    queryset = FeeItem.objects.all()
    serializer_class = FeeItemSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.prefetch_related('items').all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('student', 'institution').all()
    serializer_class = InvoiceSerializer
    filterset_class = InvoiceFilter
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'due_date', 'total_amount']
    search_fields = ['student__user__full_name', 'student__admission_number']

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.is_paid = True
        invoice.status = 'Paid'
        invoice.save()
        return Response({'status': 'Invoice marked as paid'})


class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.select_related('invoice', 'fee_item').all()
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('student', 'invoice').all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['paid_at', 'amount']
    search_fields = ['student__user__full_name', 'receipt_number', 'reference_code']


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.select_related('payment').all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]


class PenaltyViewSet(viewsets.ModelViewSet):
    queryset = Penalty.objects.select_related('student').all()
    serializer_class = PenaltySerializer
    filterset_class = PenaltyFilter
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]


class BursaryAllocationViewSet(viewsets.ModelViewSet):
    queryset = BursaryAllocation.objects.select_related('student').all()
    serializer_class = BursaryAllocationSerializer
    filterset_class = BursaryFilter
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]


class RefundRequestViewSet(viewsets.ModelViewSet):
    queryset = RefundRequest.objects.select_related('student', 'approved_by').all()
    serializer_class = RefundRequestSerializer
    filterset_class = RefundRequestFilter
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrAccountant])
    def approve(self, request, pk=None):
        refund = self.get_object()
        refund.status = 'Approved'
        refund.approved_by = request.user
        refund.refunded_on = timezone.now()
        refund.save()
        return Response({'status': 'Refund approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrAccountant])
    def reject(self, request, pk=None):
        refund = self.get_object()
        refund.status = 'Rejected'
        refund.approved_by = request.user
        refund.save()
        return Response({'status': 'Refund rejected'})


class FeeSummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]

    def get(self, request):
        institution_id = request.query_params.get('institution')
        term = request.query_params.get('term')
        year = request.query_params.get('year')

        invoices = Invoice.objects.filter(
            institution_id=institution_id,
            term=term,
            year=year
        )

        total_billed = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = Payment.objects.filter(
            invoice__in=invoices
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_penalties = Penalty.objects.filter(
            student__invoice__in=invoices
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'total_billed': total_billed,
            'total_paid': total_paid,
            'total_arrears': total_billed - total_paid,
            'total_penalties': total_penalties
        })


class FeeArrearsAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Dummy logic – replace with real analytics
        data = {
            "total_students_with_arrears": 24,
            "total_amount_due": 150000.00,
        }
        return Response(data)
    
class TopDebtorsAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # TODO: Replace this with actual logic using your Fee models
        data = [
            {"student_id": 1, "name": "John Doe", "amount_due": 5000},
            {"student_id": 2, "name": "Jane Smith", "amount_due": 4700},
        ]
        return Response(data)