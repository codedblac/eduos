from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet,
    NotificationDeliveryViewSet,
    NotificationPreferenceViewSet,
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'deliveries', NotificationDeliveryViewSet, basename='notification-deliveries')
router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preferences')

urlpatterns = [
    path('', include(router.urls)),
]
