from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Core Finance Models
router.register(r'approval-requests', views.ApprovalRequestViewSet, basename='approvalrequest')
router.register(r'anomaly-flags', views.AnomalyFlagViewSet, basename='anomalyflag')
router.register(r'budgets', views.BudgetViewSet, basename='budget')
router.register(r'expenses', views.ExpenseViewSet, basename='expense')
router.register(r'finance-notifications', views.FinanceNotificationViewSet, basename='financenotification')
router.register(r'incomes', views.IncomeViewSet, basename='income')
router.register(r'refunds', views.RefundViewSet, basename='refund')
router.register(r'scholarship-candidates', views.ScholarshipCandidateViewSet, basename='scholarshipcandidate')
router.register(r'student-finance-snapshots', views.StudentFinanceSnapshotViewSet, basename='studentfinancesnapshot')
router.register(r'student-wallets', views.StudentWalletViewSet, basename='studentwallet')
router.register(r'transaction-logs', views.TransactionLogViewSet, basename='transactionlog')
router.register(r'wallet-transactions', views.WalletTransactionViewSet, basename='wallettransaction')
router.register(r'waivers', views.WaiverViewSet, basename='waiver')

# Reference/Metadata Models (optional inclusion)
router.register(r'currencies', views.CurrencyViewSet, basename='currency')
router.register(r'fund-sources', views.FundSourceViewSet, basename='fundsource')

urlpatterns = [
    path('', include(router.urls)),
]
