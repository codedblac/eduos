from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import (
    Vehicle, Driver, TransportRoute, TransportAssignment,
    TransportAttendance, VehicleLog, TransportNotification,
    TripLog, MaintenanceRecord, TransportBooking
)
from .serializers import (
    VehicleSerializer, DriverSerializer, TransportRouteSerializer,
    TransportAssignmentSerializer, TransportAttendanceSerializer,
    VehicleLogSerializer, TransportNotificationSerializer,
    TripLogSerializer, MaintenanceRecordSerializer, TransportBookingSerializer
)
from .permissions import (
    IsInstitutionTransportStaff,
    IsTransportAdminOrReadOnly,
    IsGuardianOrStudentForTransportViewOnly
)
from institutions.permissions import IsInstitutionMember


class BaseInstitutionViewSet(viewsets.ModelViewSet):
    """
    Base class to handle common queryset + institution auto-attach.
    """
    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class VehicleViewSet(BaseInstitutionViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTransportAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['assigned_route', 'institution']
    search_fields = ['plate_number', 'model']
    ordering_fields = ['plate_number', 'capacity']


class DriverViewSet(BaseInstitutionViewSet):
    queryset = Driver.objects.select_related('user', 'assigned_vehicle')
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, IsTransportAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['assigned_vehicle', 'institution']
    search_fields = ['user__first_name', 'user__last_name']
    ordering_fields = ['user__first_name', 'license_expiry']


class TransportRouteViewSet(BaseInstitutionViewSet):
    queryset = TransportRoute.objects.all()
    serializer_class = TransportRouteSerializer
    permission_classes = [permissions.IsAuthenticated, IsTransportAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['institution', 'is_active']
    search_fields = [ 'start_location', 'end_location']
    ordering_fields = [ 'morning_time']


class TransportAssignmentViewSet(BaseInstitutionViewSet):
    queryset = TransportAssignment.objects.select_related('student', 'route')
    serializer_class = TransportAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTransportAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['student', 'route', 'is_active']
    search_fields = ['student__user__first_name', 'route__name']
    ordering_fields = ['assigned_on']


class TransportAttendanceViewSet(BaseInstitutionViewSet):
    queryset = TransportAttendance.objects.select_related('student')
    serializer_class = TransportAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTransportAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['student', 'date', 'status']
    search_fields = ['student__user__first_name']
    ordering_fields = ['date']

    @action(detail=False, methods=['post'])
    def bulk_mark_attendance(self, request):
        records = request.data.get('records', [])
        success = 0
        for record in records:
            serializer = self.get_serializer(data=record)
            if serializer.is_valid():
                serializer.save(institution=request.user.institution, recorded_by=request.user)
                success += 1
        return Response(
            {"detail": f"{success} records marked."},
            status=status.HTTP_201_CREATED
        )


class VehicleLogViewSet(BaseInstitutionViewSet):
    queryset = VehicleLog.objects.select_related('vehicle')
    serializer_class = VehicleLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsTransportAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['vehicle', 'date']
    ordering_fields = ['date']


class TransportNotificationViewSet(BaseInstitutionViewSet):
    queryset = TransportNotification.objects.select_related('student', 'recipient_guardian')
    serializer_class = TransportNotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionTransportStaff]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['type', 'student', 'is_sent']
    ordering_fields = ['sent_at']


class MaintenanceRecordViewSet(BaseInstitutionViewSet):
    queryset = MaintenanceRecord.objects.select_related('vehicle')
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsTransportAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['vehicle', 'performed_on']
    ordering_fields = ['performed_on']


class TripLogViewSet(BaseInstitutionViewSet):
    queryset = TripLog.objects.select_related('vehicle', 'driver', 'route')
    serializer_class = TripLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsTransportAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['vehicle', 'driver', 'route', 'status']
    ordering_fields = ['start_time', 'end_time']


class TransportBookingViewSet(BaseInstitutionViewSet):
    queryset = TransportBooking.objects.select_related('student', 'vehicle', 'route')
    serializer_class = TransportBookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsTransportAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['status', 'vehicle', 'route', 'student']
    ordering_fields = ['travel_date']
