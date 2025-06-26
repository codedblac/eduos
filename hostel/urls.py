# hostel/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HostelViewSet,
    HostelRoomViewSet,
    RoomAllocationViewSet,
    HostelLeaveRequestViewSet,
    HostelInspectionViewSet,
    HostelViolationViewSet,
    HostelAnnouncementViewSet
)

router = DefaultRouter()
router.register(r'hostels', HostelViewSet)
router.register(r'rooms', HostelRoomViewSet)
router.register(r'allocations', RoomAllocationViewSet)
router.register(r'leave-requests', HostelLeaveRequestViewSet)
router.register(r'inspections', HostelInspectionViewSet)
router.register(r'violations', HostelViolationViewSet)
router.register(r'announcements', HostelAnnouncementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
