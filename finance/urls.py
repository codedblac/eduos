from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Finance module endpoints
router.register(r'currencies', views.CurrencyViewSet, basename='currency')
router.register(r'fund-sources', views.FundSourceViewSet, basename='fundsource')
router.register(r'budgets', views.BudgetViewSet, basename='budget')
router.register(r'incomes', views.IncomeViewSet, basename='income')
router.register(r'expenses', views.ExpenseViewSet, basename='expense')
router.register(r'refunds', views.RefundViewSet, basename='refund')
router.register(r'waivers', views.WaiverViewSet, basename='waiver')
router.register(r'student-wallets', views.StudentWalletViewSet, basename='studentwallet')
router.register(r'wallet-transactions', views.WalletTransactionViewSet, basename='wallettransaction')
router.register(r'student-finance-snapshots', views.StudentFinanceSnapshotViewSet, basename='studentfinancesnapshot')
router.register(r'transaction-logs', views.TransactionLogViewSet, basename='transactionlog')
router.register(r'approval-requests', views.ApprovalRequestViewSet, basename='approvalrequest')
router.register(r'finance-notifications', views.FinanceNotificationViewSet, basename='financenotification')
router.register(r'anomaly-flags', views.AnomalyFlagViewSet, basename='anomalyflag')
router.register(r'scholarship-candidates', views.ScholarshipCandidateViewSet, basename='scholarshipcandidate')

urlpatterns = [
    path('', include(router.urls)),
]
