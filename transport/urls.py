# transport/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleViewSet,
    TripLogViewSet,
    MaintenanceRecordViewSet,
    TransportBookingViewSet,
    TransportDriverViewSet,
)

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'trip-logs', TripLogViewSet, basename='triplog')
router.register(r'maintenance-records', MaintenanceRecordViewSet, basename='maintenance')
router.register(r'bookings', TransportBookingViewSet, basename='booking')
router.register(r'drivers', TransportDriverViewSet, basename='driver')

urlpatterns = [
    path('', include(router.urls)),
]
