# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ItemCategoryViewSet, ItemUnitViewSet, ItemViewSet, SupplierViewSet,
    ItemStockEntryViewSet, ItemIssueViewSet, ItemReturnViewSet,
    ItemDamageViewSet, StoreRequisitionViewSet, StockAlertViewSet
)

router = DefaultRouter()
router.register(r'categories', ItemCategoryViewSet)
router.register(r'units', ItemUnitViewSet)
router.register(r'items', ItemViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'stock-entries', ItemStockEntryViewSet)
router.register(r'issues', ItemIssueViewSet)
router.register(r'returns', ItemReturnViewSet)
router.register(r'damages', ItemDamageViewSet)
router.register(r'requisitions', StoreRequisitionViewSet)
router.register(r'stock-alerts', StockAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
