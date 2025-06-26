from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet, ProcurementRequestViewSet, QuotationViewSet,
    PurchaseOrderViewSet, GoodsReceivedNoteViewSet,
    SupplierInvoiceViewSet, PaymentViewSet, TenderViewSet
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'requests', ProcurementRequestViewSet, basename='procurement-request')
router.register(r'quotations', QuotationViewSet, basename='quotation')
router.register(r'orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'grns', GoodsReceivedNoteViewSet, basename='goods-received-note')
router.register(r'invoices', SupplierInvoiceViewSet, basename='supplier-invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'tenders', TenderViewSet, basename='tender')

urlpatterns = [
    path('', include(router.urls)),
]
