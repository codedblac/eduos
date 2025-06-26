from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import (
    ItemCategory, ItemUnit, Item, Supplier,
    ItemStockEntry, ItemIssue, ItemReturn,
    ItemDamage, StoreRequisition, StockAlert
)
from .serializers import (
    ItemCategorySerializer, ItemUnitSerializer, ItemSerializer, SupplierSerializer,
    ItemStockEntrySerializer, ItemIssueSerializer, ItemReturnSerializer,
    ItemDamageSerializer, StoreRequisitionSerializer, StockAlertSerializer
)
from institutions.permissions import IsInstitutionMember


class BaseInstitutionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class ItemCategoryViewSet(BaseInstitutionViewSet):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    search_fields = ['name']


class ItemUnitViewSet(BaseInstitutionViewSet):
    queryset = ItemUnit.objects.all()
    serializer_class = ItemUnitSerializer
    search_fields = ['name', 'abbreviation']


class ItemViewSet(BaseInstitutionViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    search_fields = ['name', 'description']


class SupplierViewSet(BaseInstitutionViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    search_fields = ['name', 'contact_person']


class ItemStockEntryViewSet(BaseInstitutionViewSet):
    queryset = ItemStockEntry.objects.all()
    serializer_class = ItemStockEntrySerializer
    filterset_fields = ['item', 'supplier', 'date_received']
    ordering_fields = ['date_received']


class ItemIssueViewSet(BaseInstitutionViewSet):
    queryset = ItemIssue.objects.all()
    serializer_class = ItemIssueSerializer
    filterset_fields = ['item', 'issued_to_student', 'issued_to_user', 'date_issued']
    ordering_fields = ['date_issued']


class ItemReturnViewSet(BaseInstitutionViewSet):
    queryset = ItemReturn.objects.all()
    serializer_class = ItemReturnSerializer
    filterset_fields = ['item', 'date_returned']


class ItemDamageViewSet(BaseInstitutionViewSet):
    queryset = ItemDamage.objects.all()
    serializer_class = ItemDamageSerializer
    filterset_fields = ['item', 'date_reported']


class StoreRequisitionViewSet(BaseInstitutionViewSet):
    queryset = StoreRequisition.objects.all()
    serializer_class = StoreRequisitionSerializer
    filterset_fields = ['item', 'status', 'department', 'request_date']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        requisition = self.get_object()
        requisition.status = 'approved'
        requisition.approved_by = request.user
        requisition.save()
        return Response({'detail': 'Requisition approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        requisition = self.get_object()
        requisition.status = 'rejected'
        requisition.approved_by = request.user
        requisition.save()
        return Response({'detail': 'Requisition rejected'})


class StockAlertViewSet(BaseInstitutionViewSet):
    queryset = StockAlert.objects.all()
    serializer_class = StockAlertSerializer
    filterset_fields = ['alert_triggered']
