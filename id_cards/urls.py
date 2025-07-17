# id_cards/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IDCardTemplateViewSet,
    IDCardViewSet,
    GenerateSingleIDCardView,
    GenerateBulkIDCardsView,
    IDCardAnalyticsAPIView,
    PreviewIDCardTemplateView,
    DownloadIDCardPDFView,
)

router = DefaultRouter()
router.register(r'templates', IDCardTemplateViewSet, basename='idcard-template')
router.register(r'idcards', IDCardViewSet, basename='idcard')

urlpatterns = [
    path('', include(router.urls)),

    # Custom endpoints
    path('generate/single/<str:user_type>/<int:user_id>/', GenerateSingleIDCardView.as_view(), name='generate-single-idcard'),
    path('generate/bulk/<str:user_type>/', GenerateBulkIDCardsView.as_view(), name='generate-bulk-idcards'),
    path('analytics/', IDCardAnalyticsAPIView.as_view(), name='idcard-analytics'),
    path('preview/<int:template_id>/', PreviewIDCardTemplateView.as_view(), name='idcard-template-preview'),
    path('download/<int:pk>/', DownloadIDCardPDFView.as_view(), name='download-idcard-pdf'),
]
