from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GuardianViewSet,
    GuardianStudentLinkViewSet,
    GuardianNotificationViewSet,
    GuardianAnalyticsView,
)

router = DefaultRouter()
router.register(r'', GuardianViewSet, basename='guardian')
router.register(r'student-links', GuardianStudentLinkViewSet, basename='guardian-student-link')
router.register(r'notifications', GuardianNotificationViewSet, basename='guardian-notification')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/detail/', GuardianAnalyticsView.as_view(), name='guardian-analytics-detail'),
]
