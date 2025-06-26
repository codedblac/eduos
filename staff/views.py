# staff/views.py

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from .models import (
    Staff, StaffProfile, EmploymentHistory, StaffLeave,
    StaffDisciplinaryAction, StaffAttendance, StaffQualification
)
from .serializers import (
    StaffSerializer, StaffProfileSerializer, EmploymentHistorySerializer,
    StaffLeaveSerializer, StaffDisciplinaryActionSerializer,
    StaffAttendanceSerializer, StaffQualificationSerializer
)
from .permissions import IsHRStaffOrReadOnly, IsSelfOrHR, IsHRManager
from .filters import (
    StaffFilter, StaffProfileFilter, EmploymentHistoryFilter,
    StaffLeaveFilter, StaffDisciplinaryActionFilter,
    StaffAttendanceFilter, StaffQualificationFilter
)
from .analytics import StaffAnalytics
from .ai import StaffAIEngine


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all().select_related('user', 'institution', 'department')
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StaffFilter
    search_fields = ['user__first_name', 'user__last_name', 'job_title', 'employee_id']

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request):
        institution = request.user.institution
        analytics = StaffAnalytics(institution)

        data = {
            "staff_distribution": analytics.staff_distribution_by_type(),
            "department_staff_count": analytics.staff_count_by_department(),
            "attendance_trend": analytics.attendance_trend_last_30_days(),
            "average_attendance_rate": analytics.average_attendance_rate(),
            "top_absentees": analytics.top_absentees()
        }
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def ai_insights(self, request):
        institution = request.user.institution
        engine = StaffAIEngine(institution)

        data = {
            "staff_summary": engine.generate_summary(),
            "recommendations": engine.generate_recommendations(),
            "risk_alerts": engine.generate_risk_alerts()
        }
        return Response(data)


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all().select_related('user')
    serializer_class = StaffProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StaffProfileFilter
    search_fields = ['user__first_name', 'user__last_name', 'user__email']


class EmploymentHistoryViewSet(viewsets.ModelViewSet):
    queryset = EmploymentHistory.objects.all().select_related('staff')
    serializer_class = EmploymentHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EmploymentHistoryFilter
    search_fields = ['position', 'employment_type']


class StaffLeaveViewSet(viewsets.ModelViewSet):
    queryset = StaffLeave.objects.all().select_related('staff', 'approved_by')
    serializer_class = StaffLeaveSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrHR]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StaffLeaveFilter
    search_fields = ['leave_type', 'reason']

    @action(detail=True, methods=['post'], permission_classes=[IsHRManager])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.is_approved = True
        leave.save()
        return Response({'status': 'Leave approved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsHRManager])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.is_approved = False
        leave.save()
        return Response({'status': 'Leave rejected'}, status=status.HTTP_200_OK)


class StaffDisciplinaryActionViewSet(viewsets.ModelViewSet):
    queryset = StaffDisciplinaryAction.objects.all().select_related('staff', 'resolved_by')
    serializer_class = StaffDisciplinaryActionSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StaffDisciplinaryActionFilter
    search_fields = ['action_taken']


class StaffAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StaffAttendance.objects.all().select_related('staff')
    serializer_class = StaffAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StaffAttendanceFilter
    search_fields = ['status']


class StaffQualificationViewSet(viewsets.ModelViewSet):
    queryset = StaffQualification.objects.all().select_related('staff')
    serializer_class = StaffQualificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StaffQualificationFilter
    search_fields = ['qualification', 'institution_name']