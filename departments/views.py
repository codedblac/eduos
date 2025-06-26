from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .analytics import DepartmentAnalyticsEngine
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .ai import DepartmentAIEngine

from .models import Department, DepartmentUser, Subject
from .serializers import (
    DepartmentSerializer,
    DepartmentUserSerializer,
    SubjectSerializer
)
from .filters import DepartmentFilter, DepartmentUserFilter, SubjectFilter
from .permissions import (
    IsHOD,
    IsDeputyHOD,
    IsDepartmentMember,
    IsHODAndOwnDepartment,
    CanManageDepartmentUsers
)




@action(detail=True, methods=['get'], permission_classes=[IsHOD])
def analytics_report(self, request, pk=None):
    department = self.get_object()
    engine = DepartmentAnalyticsEngine(department)
    return Response(engine.full_report())


@action(detail=True, methods=['get'], permission_classes=[IsHOD])
def ai_dashboard(self, request, pk=None):
    department = self.get_object()
    ai = DepartmentAIEngine(department)
    return Response(ai.summary_dashboard())



class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DepartmentFilter
    search_fields = ['name', 'code']

    @action(detail=True, methods=['get'], permission_classes=[IsHODAndOwnDepartment])
    def analytics(self, request, pk=None):
        department = self.get_object()

        subjects = department.subjects.all()
        num_subjects = subjects.count()
        unassigned_subjects = subjects.filter(assigned_teacher__isnull=True).count()
        assigned_teachers = subjects.exclude(assigned_teacher__isnull=True).values('assigned_teacher').distinct().count()

        data = {
            'department': department.name,
            'total_subjects': num_subjects,
            'unassigned_subjects': unassigned_subjects,
            'assigned_teachers_count': assigned_teachers,
        }
        return Response(data)


class DepartmentUserViewSet(viewsets.ModelViewSet):
    queryset = DepartmentUser.objects.all()
    serializer_class = DepartmentUserSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageDepartmentUsers]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DepartmentUserFilter
    search_fields = ['user__first_name', 'user__last_name', 'department__name', 'role']


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SubjectFilter
    search_fields = ['name', 'code', 'department__name']

    @action(detail=False, methods=['get'], permission_classes=[IsHOD])
    def unassigned(self, request):
        queryset = Subject.objects.filter(assigned_teacher__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
