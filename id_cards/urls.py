# id_cards/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.IDCardTemplateViewSet, basename='idcard-template')
router.register(r'idcards', views.IDCardViewSet, basename='idcard')

urlpatterns = [
    path('', include(router.urls)),

    # Custom endpoints
    path('generate/single/<str:user_type>/<int:user_id>/', views.GenerateSingleIDCardView.as_view(), name='generate-single-idcard'),
    path('generate/bulk/<str:user_type>/', views.GenerateBulkIDCardsView.as_view(), name='generate-bulk-idcards'),
    path('analytics/', views.IDCardAnalyticsAPIView.as_view(), name='idcard-analytics'),
    path('preview/<int:template_id>/', views.PreviewIDCardTemplateView.as_view(), name='idcard-template-preview'),
    path('download/<int:pk>/', views.DownloadIDCardPDFView.as_view(), name='download-idcard-pdf'),
]
