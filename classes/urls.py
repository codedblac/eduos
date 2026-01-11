# classes/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClassLevelViewSet,
    StreamViewSet,
    ClassAnalyticsView,
    StreamRedistributionSuggestionView,
    ClassDistributionReportView
)

# ----------------------------
# 🚀 DRF Router
# ----------------------------
router = DefaultRouter()
router.register(r'class-levels', ClassLevelViewSet, basename='classlevel')
router.register(r'streams', StreamViewSet, basename='stream')

# ----------------------------
# 🔹 URL Patterns
# ----------------------------
urlpatterns = [
    # Core CRUD endpoints for ClassLevels and Streams
    path('', include(router.urls)),

    # Analytics endpoints
    path(
        'analytics/summary/',
        ClassAnalyticsView.as_view(),
        name='class-analytics-summary'
    ),

    # AI suggestions for balancing streams
    path(
        'ai/stream-redistribution/',
        StreamRedistributionSuggestionView.as_view(),
        name='stream-redistribution'
    ),

    # Class distribution report
    path(
        'ai/class-distribution-report/',
        ClassDistributionReportView.as_view(),
        name='class-distribution-report'
    ),
]
