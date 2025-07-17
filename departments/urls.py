from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet,
    DepartmentUserViewSet,
    SubjectViewSet,
    DepartmentAnnouncementViewSet,
    DepartmentLeaveApprovalViewSet,
    DepartmentPerformanceNoteViewSet,
    DepartmentBudgetViewSet,
    DepartmentKPIViewSet,
    DepartmentMeetingViewSet,
    DepartmentResourceViewSet,
    DepartmentAuditLogViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'department-users', DepartmentUserViewSet, basename='departmentuser')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'announcements', DepartmentAnnouncementViewSet, basename='announcement')
router.register(r'leave-approvals', DepartmentLeaveApprovalViewSet, basename='leaveapproval')
router.register(r'performance-notes', DepartmentPerformanceNoteViewSet, basename='performancenote')
router.register(r'budgets', DepartmentBudgetViewSet, basename='departmentbudget')
router.register(r'kpis', DepartmentKPIViewSet, basename='departmentkpi')
router.register(r'meetings', DepartmentMeetingViewSet, basename='departmentmeeting')
router.register(r'resources', DepartmentResourceViewSet, basename='departmentresource')
router.register(r'audit-logs', DepartmentAuditLogViewSet, basename='departmentauditlog')

urlpatterns = [
    path('', include(router.urls)),
]
