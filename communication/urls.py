from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CommunicationAnnouncementViewSet,
    CommunicationTargetViewSet,
    CommunicationReadLogViewSet,
    CommunicationLogViewSet,
    AnnouncementCategoryViewSet,
)

router = DefaultRouter()
router.register(r'announcements', CommunicationAnnouncementViewSet, basename='announcement')
router.register(r'targets', CommunicationTargetViewSet, basename='target')
router.register(r'read-logs', CommunicationReadLogViewSet, basename='read-log')
router.register(r'logs', CommunicationLogViewSet, basename='log')
router.register(r'categories', AnnouncementCategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
