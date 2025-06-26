from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import (
    Vehicle, Driver, TransportRoute,
    StudentTransportAssignment, TransportAttendance
)
from .serializers import (
    VehicleSerializer, DriverSerializer, TransportRouteSerializer,
    StudentTransportAssignmentSerializer, TransportAttendanceSerializer
)
from institutions.permissions import IsInstitutionMember
from students.models import Student


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['status', 'institution']
    search_fields = ['name', 'registration_number']
    ordering_fields = ['name', 'capacity']

    def get_queryset(self):
        return Vehicle.objects.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['vehicle', 'institution']
    search_fields = ['user__full_name', 'user__email']
    ordering_fields = ['user__full_name']

    def get_queryset(self):
        return Driver.objects.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class TransportRouteViewSet(viewsets.ModelViewSet):
    queryset = TransportRoute.objects.all()
    serializer_class = TransportRouteSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['institution']
    search_fields = ['name', 'vehicle__name']
    ordering_fields = ['name']

    def get_queryset(self):
        return TransportRoute.objects.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class StudentTransportAssignmentViewSet(viewsets.ModelViewSet):
    queryset = StudentTransportAssignment.objects.all()
    serializer_class = StudentTransportAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['student', 'vehicle', 'route', 'is_active']
    search_fields = ['student__user__full_name', 'route__name']
    ordering_fields = ['pickup_time']

    def get_queryset(self):
        return StudentTransportAssignment.objects.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class TransportAttendanceViewSet(viewsets.ModelViewSet):
    queryset = TransportAttendance.objects.all()
    serializer_class = TransportAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['student', 'date', 'status', 'vehicle', 'route']
    search_fields = ['student__user__full_name', 'route__name']
    ordering_fields = ['date']

    def get_queryset(self):
        return TransportAttendance.objects.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)

    @action(detail=False, methods=['post'])
    def bulk_mark_attendance(self, request):
        data = request.data.get('records', [])
        for entry in data:
            serializer = TransportAttendanceSerializer(data=entry)
            if serializer.is_valid():
                serializer.save(institution=request.user.institution)
        return Response({'detail': 'Attendance processed.'}, status=status.HTTP_201_CREATED)
