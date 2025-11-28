from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .ai import DepartmentAIEngine
from .analytics import DepartmentAnalyticsEngine
from .models import (
    Department, DepartmentUser, Subject, DepartmentAnnouncement,
    DepartmentLeaveApproval, DepartmentPerformanceNote, DepartmentBudget,
    DepartmentKPI, DepartmentMeeting, DepartmentResource, DepartmentAuditLog
)
from .serializers import (
    DepartmentSerializer, DepartmentCreateUpdateSerializer,
    DepartmentUserSerializer, DepartmentUserCreateUpdateSerializer,
    SubjectSerializer, SubjectCreateUpdateSerializer,
    DepartmentAnnouncementSerializer, DepartmentAnnouncementCreateSerializer,
    DepartmentLeaveApprovalSerializer, DepartmentLeaveApprovalCreateSerializer,
    DepartmentPerformanceNoteSerializer, DepartmentPerformanceNoteCreateSerializer,
    DepartmentBudgetSerializer, DepartmentBudgetCreateSerializer,
    DepartmentKPISerializer, DepartmentKPICreateSerializer,
    DepartmentMeetingSerializer, DepartmentMeetingCreateSerializer,
    DepartmentResourceSerializer, DepartmentResourceCreateSerializer,
    DepartmentAuditLogSerializer
)
from .filters import (
    DepartmentFilter, DepartmentUserFilter, SubjectFilter
)
from .permissions import (
    IsHOD,
    IsDeputyHOD,
    IsDepartmentMember,
    IsHODAndOwnDepartment,
    CanManageDepartmentUsers
)


# --- Department ViewSet ---

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DepartmentFilter
    search_fields = ['name', 'code']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentCreateUpdateSerializer
        return DepartmentSerializer

    @action(detail=True, methods=['get'], permission_classes=[IsHODAndOwnDepartment])
    def analytics(self, request, pk=None):
        department = self.get_object()
        engine = DepartmentAnalyticsEngine(department)
        return Response(engine.full_report())

    @action(detail=True, methods=['get'], permission_classes=[IsHODAndOwnDepartment])
    def ai_dashboard(self, request, pk=None):
        department = self.get_object()
        ai = DepartmentAIEngine(department)
        return Response(ai.summary_dashboard())


# --- DepartmentUser ViewSet ---

class DepartmentUserViewSet(viewsets.ModelViewSet):
    queryset = DepartmentUser.objects.select_related('user', 'department')
    permission_classes = [permissions.IsAuthenticated, CanManageDepartmentUsers]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DepartmentUserFilter
    search_fields = ['user__first_name', 'user__last_name', 'department__name', 'role']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentUserCreateUpdateSerializer
        return DepartmentUserSerializer


# --- Subject ViewSet ---

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related('department')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SubjectFilter
    search_fields = ['name', 'code', 'department__name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubjectCreateUpdateSerializer
        return SubjectSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsHOD])
    def unassigned(self, request):
        queryset = Subject.objects.filter(assigned_teacher__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# --- DepartmentAnnouncement ViewSet ---

class DepartmentAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = DepartmentAnnouncement.objects.select_related('department', 'created_by')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'department__name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentAnnouncementCreateSerializer
        return DepartmentAnnouncementSerializer


# --- DepartmentLeaveApproval ViewSet ---

class DepartmentLeaveApprovalViewSet(viewsets.ModelViewSet):
    queryset = DepartmentLeaveApproval.objects.select_related('department', 'staff_member')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentLeaveApprovalCreateSerializer
        return DepartmentLeaveApprovalSerializer


# --- DepartmentPerformanceNote ViewSet ---

class DepartmentPerformanceNoteViewSet(viewsets.ModelViewSet):
    queryset = DepartmentPerformanceNote.objects.select_related('department', 'student', 'created_by')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentPerformanceNoteCreateSerializer
        return DepartmentPerformanceNoteSerializer


# --- DepartmentBudget ViewSet ---

class DepartmentBudgetViewSet(viewsets.ModelViewSet):
    queryset = DepartmentBudget.objects.select_related('department')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentBudgetCreateSerializer
        return DepartmentBudgetSerializer


# --- DepartmentKPI ViewSet ---

class DepartmentKPIViewSet(viewsets.ModelViewSet):
    queryset = DepartmentKPI.objects.select_related('department', 'term')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentKPICreateSerializer
        return DepartmentKPISerializer


# --- DepartmentMeeting ViewSet ---

class DepartmentMeetingViewSet(viewsets.ModelViewSet):
    queryset = DepartmentMeeting.objects.select_related('department', 'conducted_by')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentMeetingCreateSerializer
        return DepartmentMeetingSerializer


# --- DepartmentResource ViewSet ---

class DepartmentResourceViewSet(viewsets.ModelViewSet):
    queryset = DepartmentResource.objects.select_related('department')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentResourceCreateSerializer
        return DepartmentResourceSerializer


# --- DepartmentAuditLog ViewSet (ReadOnly) ---

class DepartmentAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepartmentAuditLog.objects.select_related('department', 'actor')
    serializer_class = DepartmentAuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['action', 'actor__first_name', 'actor__last_name']
