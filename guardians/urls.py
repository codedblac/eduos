from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuardianViewSet, GuardianStudentLinkViewSet, GuardianNotificationViewSet

router = DefaultRouter()
router.register('guardians', GuardianViewSet)
router.register('student-links', GuardianStudentLinkViewSet)
router.register('notifications', GuardianNotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
