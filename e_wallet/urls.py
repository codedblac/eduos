# e_wallet/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from e_wallet.views import (
    WalletViewSet,
    WalletTransactionViewSet,
    MicroFeeViewSet,
    MicroFeePaymentViewSet,
    WalletTopUpRequestViewSet,
    WalletPolicyViewSet,
)

router = DefaultRouter()
router.register(r'wallets', WalletViewSet, basename='wallets')
router.register(r'transactions', WalletTransactionViewSet, basename='transactions')
router.register(r'micro-fees', MicroFeeViewSet, basename='microfees')
router.register(r'micro-fee-payments', MicroFeePaymentViewSet, basename='microfeepayments')
router.register(r'topup-requests', WalletTopUpRequestViewSet, basename='topuprequests')
router.register(r'policies', WalletPolicyViewSet, basename='walletpolicies')

urlpatterns = [
    path('', include(router.urls)),
]
