from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from .models import (
    SchoolAttendanceRecord,
    ClassAttendanceRecord,
    AbsenceReason
)
from .serializers import (
    SchoolAttendanceSerializer,
    ClassAttendanceSerializer,
    AbsenceReasonSerializer
)


class BaseInstitutionViewSet(viewsets.ModelViewSet):
    """
    Reusable base class to enforce institution filtering and assignment.
    """
    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(
            institution=self.request.user.institution,
            recorded_by=self.request.user
        )


class SchoolAttendanceViewSet(BaseInstitutionViewSet):
    queryset = SchoolAttendanceRecord.objects.all().order_by('-date')
    serializer_class = SchoolAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClassAttendanceViewSet(BaseInstitutionViewSet):
    queryset = ClassAttendanceRecord.objects.all().order_by('-date')
    serializer_class = ClassAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]


class AbsenceReasonViewSet(BaseInstitutionViewSet):
    queryset = AbsenceReason.objects.all()
    serializer_class = AbsenceReasonSerializer
    permission_classes = [permissions.IsAuthenticated]
