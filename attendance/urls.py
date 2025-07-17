from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolAttendanceViewSet,
    ClassAttendanceViewSet,
    AbsenceReasonViewSet,
)

router = DefaultRouter()

# Register core attendance endpoints
router.register(r'school-attendance', SchoolAttendanceViewSet, basename='school-attendance')
router.register(r'class-attendance', ClassAttendanceViewSet, basename='class-attendance')
router.register(r'absence-reasons', AbsenceReasonViewSet, basename='absence-reason')

urlpatterns = [
    path('', include(router.urls)),
]
