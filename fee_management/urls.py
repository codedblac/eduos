from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'fee-items', views.FeeItemViewSet)
router.register(r'fee-structures', views.FeeStructureViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'invoice-items', views.InvoiceItemViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'receipts', views.ReceiptViewSet)
router.register(r'penalties', views.PenaltyViewSet)
router.register(r'bursaries', views.BursaryAllocationViewSet)
router.register(r'refunds', views.RefundRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # 📊 Custom analytics and financial summary endpoints
    path('analytics/summary/', views.FeeSummaryView.as_view(), name='fee-summary'),
    path('analytics/arrears/', views.FeeArrearsAnalyticsView.as_view(), name='fee-arrears'),
    path('analytics/top-debtors/', views.TopDebtorsAnalyticsView.as_view(), name='top-debtors'),
]
