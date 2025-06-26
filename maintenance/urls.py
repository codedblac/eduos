from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EquipmentViewSet,
    MaintenanceRequestViewSet,
    MaintenanceScheduleViewSet,
    MaintenanceLogViewSet,
)

router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet)
router.register(r'requests', MaintenanceRequestViewSet)
router.register(r'schedules', MaintenanceScheduleViewSet)
router.register(r'logs', MaintenanceLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
