from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import (
    Supplier, ProcurementRequest, Quotation, PurchaseOrder,
    GoodsReceivedNote, SupplierInvoice, Payment, Tender
)
from .serializers import (
    SupplierSerializer, ProcurementRequestReadSerializer, ProcurementRequestWriteSerializer,
    QuotationSerializer, PurchaseOrderSerializer, GoodsReceivedNoteSerializer,
    SupplierInvoiceSerializer, PaymentSerializer, TenderSerializer
)
from .filters import (
    ProcurementRequestFilter, PurchaseOrderFilter, SupplierInvoiceFilter,
    GoodsReceivedNoteFilter, TenderFilter
)
from .permissions import (
    IsInstitutionMember, IsProcurementOfficer, IsFinanceManager,
    IsDepartmentHead, IsStoreClerk, IsRequestOwnerOrAdmin
)
from .ai import ProcurementAIEngine
from .analytics import ProcurementAnalyticsEngine

# ----------------------------
# Supplier ViewSet
# ----------------------------
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsInstitutionMember, IsProcurementOfficer]

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)


# ----------------------------
# Procurement Request ViewSet
# ----------------------------
class ProcurementRequestViewSet(viewsets.ModelViewSet):
    queryset = ProcurementRequest.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProcurementRequestFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ProcurementRequestWriteSerializer
        return ProcurementRequestReadSerializer

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsInstitutionMember(), IsDepartmentHead()]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsInstitutionMember(), IsRequestOwnerOrAdmin()]
        return [IsInstitutionMember()]

    @action(detail=False, methods=['get'], url_path='ai/predict-price')
    def predict_price(self, request):
        item = request.query_params.get('item')
        ai = ProcurementAIEngine(institution_id=request.user.institution_id)
        price = ai.predict_price(item)
        return Response({"item": item, "predicted_price": price})

    @action(detail=False, methods=['get'], url_path='ai/recommend-suppliers')
    def recommend_suppliers(self, request):
        item = request.query_params.get('item')
        ai = ProcurementAIEngine(institution_id=request.user.institution_id)
        results = ai.recommend_suppliers(item)
        return Response(results)

    @action(detail=False, methods=['get'], url_path='analytics/summary')
    def analytics_summary(self, request):
        analytics = ProcurementAnalyticsEngine(institution_id=request.user.institution_id)
        data = analytics.get_summary()
        return Response(data)


# ----------------------------
# Quotation ViewSet
# ----------------------------
class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    permission_classes = [IsInstitutionMember, IsProcurementOfficer]

    def get_queryset(self):
        return self.queryset.filter(request__institution=self.request.user.institution)


# ----------------------------
# Purchase Order ViewSet
# ----------------------------
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PurchaseOrderFilter
    permission_classes = [IsInstitutionMember, IsProcurementOfficer]

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)


# ----------------------------
# Goods Received Note ViewSet
# ----------------------------
class GoodsReceivedNoteViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceivedNote.objects.all()
    serializer_class = GoodsReceivedNoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GoodsReceivedNoteFilter
    permission_classes = [IsInstitutionMember, IsStoreClerk]

    def get_queryset(self):
        return self.queryset.filter(po__institution=self.request.user.institution)


# ----------------------------
# Supplier Invoice ViewSet
# ----------------------------
class SupplierInvoiceViewSet(viewsets.ModelViewSet):
    queryset = SupplierInvoice.objects.all()
    serializer_class = SupplierInvoiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SupplierInvoiceFilter
    permission_classes = [IsInstitutionMember, IsFinanceManager]

    def get_queryset(self):
        return self.queryset.filter(po__institution=self.request.user.institution)


# ----------------------------
# Payment ViewSet
# ----------------------------
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsInstitutionMember, IsFinanceManager]

    def get_queryset(self):
        return self.queryset.filter(invoice__po__institution=self.request.user.institution)


# ----------------------------
# Tender ViewSet
# ----------------------------
class TenderViewSet(viewsets.ModelViewSet):
    queryset = Tender.objects.all()
    serializer_class = TenderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TenderFilter
    permission_classes = [IsInstitutionMember, IsProcurementOfficer]

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    @action(detail=False, methods=['get'], url_path='analytics/top-suppliers')
    def top_suppliers(self, request):
        analytics = ProcurementAnalyticsEngine(institution_id=request.user.institution_id)
        data = analytics.spending_by_supplier()
        return Response(data)

    @action(detail=False, methods=['get'], url_path='ai/anomalies')
    def detect_anomalies(self, request):
        ai = ProcurementAIEngine(institution_id=request.user.institution_id)
        anomalies = ai.detect_anomalies()
        return Response({"anomalies": anomalies})
