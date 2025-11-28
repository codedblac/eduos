from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Hostel, HostelRoom, RoomAllocation,
    HostelLeaveRequest, HostelInspection,
    HostelViolation, HostelAnnouncement
)
from .serializers import (
    HostelSerializer, HostelRoomSerializer,
    RoomAllocationSerializer, HostelLeaveRequestSerializer,
    HostelInspectionSerializer, HostelViolationSerializer,
    HostelAnnouncementSerializer
)
from institutions.permissions import IsInstitutionMember


class BaseInstitutionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class HostelViewSet(BaseInstitutionViewSet):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    search_fields = [ 'description']
    ordering_fields = [ 'capacity']


class HostelRoomViewSet(BaseInstitutionViewSet):
    queryset = HostelRoom.objects.all()
    serializer_class = HostelRoomSerializer
    filterset_fields = ['hostel', 'floor', 'room_type']
    search_fields = []


class RoomAllocationViewSet(BaseInstitutionViewSet):
    queryset = RoomAllocation.objects.all()
    serializer_class = RoomAllocationSerializer
    filterset_fields = ['student', 'room', 'is_active']


class HostelLeaveRequestViewSet(BaseInstitutionViewSet):
    queryset = HostelLeaveRequest.objects.all()
    serializer_class = HostelLeaveRequestSerializer
    filterset_fields = ['approved', 'leave_date', 'return_date']
    search_fields = ['reason']


class HostelInspectionViewSet(BaseInstitutionViewSet):
    queryset = HostelInspection.objects.all()
    serializer_class = HostelInspectionSerializer
    filterset_fields = ['room', 'inspected_by', 'date']


class HostelViolationViewSet(BaseInstitutionViewSet):
    queryset = HostelViolation.objects.all()
    serializer_class = HostelViolationSerializer
    filterset_fields = ['room', 'resolved']
    search_fields = ['description', 'action_taken']


class HostelAnnouncementViewSet(BaseInstitutionViewSet):
    queryset = HostelAnnouncement.objects.all()
    serializer_class = HostelAnnouncementSerializer
    filterset_fields = ['target_hostel']
    search_fields = ['title', 'message']
