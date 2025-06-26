from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import (
    VisitorLog, Appointment, ParcelDelivery, GatePass,
    FrontDeskTicket, FrontAnnouncement, SecurityLog
)
from .serializers import (
    VisitorLogSerializer, AppointmentSerializer, ParcelDeliverySerializer,
    GatePassSerializer, FrontDeskTicketSerializer,
    FrontAnnouncementSerializer, SecurityLogSerializer
)
from .permissions import (
    IsInstitutionStaffOrReadOnly,
    IsOwnerOrReadOnly,
    IsSecurityStaff,
    IsFrontDeskStaff
)
from .filters import (
    VisitorLogFilter,
    AppointmentFilter,
    ParcelDeliveryFilter,
    GatePassFilter,
    FrontDeskTicketFilter,
    FrontAnnouncementFilter,
    SecurityLogFilter
)
from .analytics import FrontOfficeAnalyticsEngine


class VisitorLogViewSet(viewsets.ModelViewSet):
    queryset = VisitorLog.objects.all()
    serializer_class = VisitorLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsFrontDeskStaff | IsInstitutionStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = VisitorLogFilter
    search_fields = ['visitor_name', 'id_type', 'vehicle_plate']


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly | IsInstitutionStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AppointmentFilter
    search_fields = ['visitor_name', 'meeting_with__email']


class ParcelDeliveryViewSet(viewsets.ModelViewSet):
    queryset = ParcelDelivery.objects.all()
    serializer_class = ParcelDeliverySerializer
    permission_classes = [permissions.IsAuthenticated, IsFrontDeskStaff | IsInstitutionStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ParcelDeliveryFilter
    search_fields = ['sender_name', 'parcel_description']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_picked(self, request, pk=None):
        delivery = self.get_object()
        if delivery.status != 'picked':
            delivery.status = 'picked'
            delivery.picked_on = timezone.now()
            delivery.save()
            return Response({'status': 'Parcel marked as picked.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Parcel already marked as picked.'}, status=status.HTTP_400_BAD_REQUEST)


class GatePassViewSet(viewsets.ModelViewSet):
    queryset = GatePass.objects.all()
    serializer_class = GatePassSerializer
    permission_classes = [permissions.IsAuthenticated, IsSecurityStaff | IsInstitutionStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = GatePassFilter
    search_fields = ['reason']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        gate_pass = self.get_object()
        gate_pass.status = 'approved'
        gate_pass.approved_by = request.user
        gate_pass.approved_on = timezone.now()
        gate_pass.save()
        return Response({'status': 'Gate pass approved.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        gate_pass = self.get_object()
        gate_pass.status = 'rejected'
        gate_pass.approved_by = request.user
        gate_pass.approved_on = timezone.now()
        gate_pass.save()
        return Response({'status': 'Gate pass rejected.'}, status=status.HTTP_200_OK)


class FrontDeskTicketViewSet(viewsets.ModelViewSet):
    queryset = FrontDeskTicket.objects.all()
    serializer_class = FrontDeskTicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = FrontDeskTicketFilter
    search_fields = ['description']


class FrontAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = FrontAnnouncement.objects.all()
    serializer_class = FrontAnnouncementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = FrontAnnouncementFilter
    search_fields = ['message']


class SecurityLogViewSet(viewsets.ModelViewSet):
    queryset = SecurityLog.objects.all()
    serializer_class = SecurityLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsSecurityStaff | IsInstitutionStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SecurityLogFilter
    search_fields = ['person_name', 'vehicle_plate']


# AI-powered dashboard view
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def front_office_dashboard(request):
    institution = request.user.institution
    engine = FrontOfficeAnalyticsEngine(institution)
    return Response(engine.get_full_dashboard())
