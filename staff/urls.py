# staff/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StaffViewSet,
    StaffProfileViewSet,
    EmploymentHistoryViewSet,
    StaffLeaveViewSet,
    StaffDisciplinaryActionViewSet,
    StaffAttendanceViewSet,
    StaffQualificationViewSet,
)

router = DefaultRouter()
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'staff-profiles', StaffProfileViewSet, basename='staff-profile')
router.register(r'employment-history', EmploymentHistoryViewSet, basename='employment-history')
router.register(r'leaves', StaffLeaveViewSet, basename='staff-leave')
router.register(r'disciplinary-actions', StaffDisciplinaryActionViewSet, basename='disciplinary-action')
router.register(r'attendance', StaffAttendanceViewSet, basename='staff-attendance')
router.register(r'qualifications', StaffQualificationViewSet, basename='staff-qualification')

urlpatterns = [
    path('', include(router.urls)),
]
