from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    MedicalFlagViewSet,
    StudentAnalyticsDashboardView
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'medical-flags', MedicalFlagViewSet, basename='medical-flag')

urlpatterns = [
    path('', include(router.urls)),

    # Analytics Dashboard
    path('analytics/students/', StudentAnalyticsDashboardView.as_view(), name='student-analytics-dashboard'),
]
