from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleViewSet,
    DriverViewSet,
    TransportRouteViewSet,
    TransportAssignmentViewSet,
    TransportAttendanceViewSet,
    TransportBookingViewSet,
    TripLogViewSet,
    MaintenanceRecordViewSet,
    TransportNotificationViewSet,
)

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'routes', TransportRouteViewSet, basename='transport-route')
router.register(r'assignments', TransportAssignmentViewSet, basename='transport-assignment')
router.register(r'attendance', TransportAttendanceViewSet, basename='transport-attendance')
router.register(r'bookings', TransportBookingViewSet, basename='transport-booking')
router.register(r'trip-logs', TripLogViewSet, basename='trip-log')
router.register(r'maintenance-records', MaintenanceRecordViewSet, basename='maintenance-record')
router.register(r'notifications', TransportNotificationViewSet, basename='transport-notification')

urlpatterns = [
    path('', include(router.urls)),
]
