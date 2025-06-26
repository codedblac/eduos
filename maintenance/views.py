from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Equipment,
    MaintenanceRequest,
    MaintenanceSchedule,
    MaintenanceLog
)
from .serializers import (
    EquipmentSerializer,
    MaintenanceRequestSerializer,
    MaintenanceScheduleSerializer,
    MaintenanceLogSerializer
)
from .filters import (
    EquipmentFilter,
    MaintenanceRequestFilter,
    MaintenanceScheduleFilter,
    MaintenanceLogFilter
)
from .permissions import IsInstitutionStaffOrReadOnly


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EquipmentFilter
    search_fields = ['name', 'type', 'location']
    ordering_fields = ['name', 'status', 'created_at']


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MaintenanceRequestFilter
    search_fields = ['equipment__name', 'description']
    ordering_fields = ['reported_on', 'status', 'priority']


class MaintenanceScheduleViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceSchedule.objects.all()
    serializer_class = MaintenanceScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MaintenanceScheduleFilter
    search_fields = ['equipment__name', 'frequency']
    ordering_fields = ['next_maintenance_date', 'frequency']


class MaintenanceLogViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MaintenanceLogFilter
    search_fields = ['equipment__name', 'notes']
    ordering_fields = ['performed_on', 'cost']
