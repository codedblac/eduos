from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import (
    DisciplineCategory,
    DisciplineCase,
    DisciplinaryAction
)
from .serializers import (
    DisciplineCategorySerializer,
    DisciplineCaseSerializer,
    DisciplinaryActionSerializer
)


class BaseInstitutionViewSet(viewsets.ModelViewSet):
    """
    Ensures institution-specific data isolation and attribution.
    """
    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(
            institution=self.request.user.institution,
            reported_by=getattr(self.request.user, 'user', self.request.user)
        )


class DisciplineCategoryViewSet(BaseInstitutionViewSet):
    queryset = DisciplineCategory.objects.all()
    serializer_class = DisciplineCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class DisciplineCaseViewSet(BaseInstitutionViewSet):
    queryset = DisciplineCase.objects.all().order_by('-incident_date')
    serializer_class = DisciplineCaseSerializer
    permission_classes = [permissions.IsAuthenticated]


class DisciplinaryActionViewSet(viewsets.ModelViewSet):
    queryset = DisciplinaryAction.objects.all().order_by('-date_assigned')
    serializer_class = DisciplinaryActionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)
