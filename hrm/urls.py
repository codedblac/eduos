from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobPostingViewSet, JobApplicationViewSet, DepartmentViewSet,
    SchoolBranchViewSet, StaffHRRecordViewSet, ContractViewSet,
    LeaveTypeViewSet, LeaveRequestViewSet, AttendanceRecordViewSet,
    PerformanceReviewViewSet, DisciplinaryActionViewSet,
    HRDocumentViewSet, HRMAnalyticsViewSet, HRMAIInsightsViewSet
)

router = DefaultRouter()
router.register(r'job-postings', JobPostingViewSet, basename='job-posting')
router.register(r'applications', JobApplicationViewSet, basename='job-application')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'branches', SchoolBranchViewSet, basename='school-branch')
router.register(r'staff', StaffHRRecordViewSet, basename='staff-hr-record')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'performance-reviews', PerformanceReviewViewSet, basename='performance-review')
router.register(r'disciplinary-actions', DisciplinaryActionViewSet, basename='disciplinary-action')
router.register(r'documents', HRDocumentViewSet, basename='hr-document')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', HRMAnalyticsViewSet.as_view({'get': 'list'}), name='hrm-analytics'),
    path('ai-insights/', HRMAIInsightsViewSet.as_view({'get': 'list'}), name='hrm-ai-insights'),
]
