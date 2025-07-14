# teachers/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeacherViewSet,
    TeacherAnalyticsView,
)

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teacher')

urlpatterns = [
    path('', include(router.urls)),
    path('teachers/analytics/', TeacherAnalyticsView.as_view(), name='teacher-analytics'),
]
