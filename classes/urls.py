from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClassLevelViewSet,
    StreamViewSet,
    ClassAnalyticsView,
    StreamRedistributionSuggestionView,
    ClassDistributionReportView
)

router = DefaultRouter()
router.register(r'class-levels', ClassLevelViewSet, basename='classlevel')
router.register(r'streams', StreamViewSet, basename='stream')

urlpatterns = [
    # Core CRUD endpoints
    path('', include(router.urls)),

    # Analytics and AI endpoints
    path('analytics/summary/', ClassAnalyticsView.as_view(), name='class-analytics-summary'),
    path('ai/stream-redistribution/', StreamRedistributionSuggestionView.as_view(), name='stream-redistribution'),
    path('ai/class-distribution-report/', ClassDistributionReportView.as_view(), name='class-distribution-report'),
]
