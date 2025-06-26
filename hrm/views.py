from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    JobPosting, JobApplication, StaffHRRecord, Contract,
    Department, SchoolBranch, LeaveType, LeaveRequest,
    AttendanceRecord, PerformanceReview, DisciplinaryAction, HRDocument
)

from .serializers import (
    JobPostingSerializer, JobApplicationSerializer, StaffHRRecordSerializer,
    ContractSerializer, DepartmentSerializer, SchoolBranchSerializer,
    LeaveTypeSerializer, LeaveRequestSerializer, AttendanceRecordSerializer,
    PerformanceReviewSerializer, DisciplinaryActionSerializer, HRDocumentSerializer
)

from .permissions import IsHRManager
from .filters import (
    StaffHRRecordFilter, JobPostingFilter, JobApplicationFilter,
    ContractFilter, LeaveRequestFilter, AttendanceRecordFilter,
    PerformanceReviewFilter, DisciplinaryActionFilter, HRDocumentFilter
)

from .ai import HRMAIEngine
from .analytics import HRMAnalyticsEngine


class StaffHRRecordViewSet(viewsets.ModelViewSet):
    queryset = StaffHRRecord.objects.select_related('user', 'department', 'branch', 'role').all()
    serializer_class = StaffHRRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StaffHRRecordFilter
    search_fields = ['user__first_name', 'user__last_name', 'designation']


class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobPostingFilter


class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.select_related('job').all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobApplicationFilter


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]


class SchoolBranchViewSet(viewsets.ModelViewSet):
    queryset = SchoolBranch.objects.all()
    serializer_class = SchoolBranchSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related('staff', 'staff__user').all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ContractFilter


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('staff', 'leave_type').all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LeaveRequestFilter


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related('staff', 'staff__user').all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AttendanceRecordFilter


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReview.objects.select_related('staff', 'staff__user', 'reviewer').all()
    serializer_class = PerformanceReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PerformanceReviewFilter


class DisciplinaryActionViewSet(viewsets.ModelViewSet):
    queryset = DisciplinaryAction.objects.select_related('staff', 'staff__user', 'added_by').all()
    serializer_class = DisciplinaryActionSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DisciplinaryActionFilter


class HRDocumentViewSet(viewsets.ModelViewSet):
    queryset = HRDocument.objects.select_related('staff', 'staff__user').all()
    serializer_class = HRDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]
    filter_backends = [DjangoFilterBackend]
    filterset_class = HRDocumentFilter


class HRMAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsHRManager]

    def list(self, request):
        engine = HRMAnalyticsEngine(institution=request.user.institution)
        data = engine.current_summary()
        return Response(data)


class HRMAIInsightsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsHRManager]

    def list(self, request):
        ai = HRMAIEngine(institution=request.user.institution)
        insights = {
            "contract_expiry_alerts": ai.expiring_contracts_alerts(),
            "performance_anomalies": ai.detect_performance_anomalies(),
            "attrition_risk": ai.predict_attrition_risk(),
            "leave_issues": ai.leave_balance_issues(),
        }
        return Response(insights)
