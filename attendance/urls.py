from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolAttendanceViewSet,
    ClassAttendanceViewSet,
    AbsenceReasonViewSet
)

router = DefaultRouter()
router.register(r'school', SchoolAttendanceViewSet, basename='school-attendance')
router.register(r'class', ClassAttendanceViewSet, basename='class-attendance')
router.register(r'reasons', AbsenceReasonViewSet, basename='absence-reasons')

urlpatterns = [
    path('', include(router.urls)),
]
