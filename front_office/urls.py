from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VisitorLogViewSet,
    AppointmentViewSet,
    ParcelDeliveryViewSet,
    GatePassViewSet,
    FrontDeskTicketViewSet,
    FrontAnnouncementViewSet,
    SecurityLogViewSet,
    front_office_dashboard  # added dashboard view
)

router = DefaultRouter()
router.register('visitors', VisitorLogViewSet, basename='visitorlog')
router.register('appointments', AppointmentViewSet, basename='appointment')
router.register('parcels', ParcelDeliveryViewSet, basename='parceldelivery')
router.register('gatepasses', GatePassViewSet, basename='gatepass')
router.register('tickets', FrontDeskTicketViewSet, basename='frontdeskticket')
router.register('announcements', FrontAnnouncementViewSet, basename='frontannouncement')
router.register('security-logs', SecurityLogViewSet, basename='securitylog')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', front_office_dashboard, name='front-office-dashboard'),  # new endpoint
]
