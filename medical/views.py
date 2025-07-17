from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from django.db.models import Count
from .models import SickBayVisit, MedicalFlag, MedicineInventory
from .serializers import (
    MedicalVisitSerializer,
    DispensedMedicineSerializer,
    MedicineInventorySerializer
)
from .permissions import (
    IsMedicalStaff,
    IsAdminOrMedicalStaff,
    CanManageInventory,
    CanViewHealthAnalytics,
)
from students.models import Student


# ------------------------------
# Sick Bay Visit
# ------------------------------

class SickBayVisitCreateView(generics.CreateAPIView):
    queryset = SickBayVisit.objects.all()
    serializer_class = MedicalVisitSerializer
    permission_classes = [permissions.IsAuthenticated, IsMedicalStaff]


class SickBayVisitListView(generics.ListAPIView):
    queryset = SickBayVisit.objects.select_related('student', 'recorded_by').all()
    serializer_class = MedicalVisitSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMedicalStaff]


# ------------------------------
# Medical Flag Management
# ------------------------------

class MedicalFlagCreateView(generics.CreateAPIView):
    queryset = MedicalFlag.objects.all()
    serializer_class = DispensedMedicineSerializer
    permission_classes = [permissions.IsAuthenticated, IsMedicalStaff]


class MedicalFlagListView(generics.ListAPIView):
    queryset = MedicalFlag.objects.select_related('student').all()
    serializer_class = DispensedMedicineSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrMedicalStaff]


# ------------------------------
# Medicine Inventory Management
# ------------------------------

class MedicineInventoryListCreateView(generics.ListCreateAPIView):
    queryset = MedicineInventory.objects.all()
    serializer_class = MedicineInventorySerializer
    permission_classes = [permissions.IsAuthenticated, CanManageInventory]


class MedicineInventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MedicineInventory.objects.all()
    serializer_class = MedicineInventorySerializer
    permission_classes = [permissions.IsAuthenticated, CanManageInventory]


# ------------------------------
# AI-Powered Health Insights
# ------------------------------

class AffectedClassesAnalyticsView(views.APIView):
    """
    AI-Driven: Returns most affected classes by illness trends.
    """
    permission_classes = [permissions.IsAuthenticated, CanViewHealthAnalytics]

    def get(self, request):
        data = (
            SickBayVisit.objects.values('student__class_level__name', 'student__stream__name')
            .annotate(visits=Count('id'))
            .order_by('-visits')[:5]
        )

        results = []
        for entry in data:
            results.append({
                "class_level": entry['student__class_level__name'],
                "stream": entry['student__stream__name'],
                "visit_count": entry['visits'],
            })

        return Response({
            "top_affected_classes": results,
            "detail": "This data represents the most affected classes by medical visits."
        })


class CommonSymptomsAnalyticsView(views.APIView):
    """
    AI-Driven: Returns the most common symptoms recorded.
    """
    permission_classes = [permissions.IsAuthenticated, CanViewHealthAnalytics]

    def get(self, request):
        symptoms = (
            SickBayVisit.objects.values('symptoms')
            .annotate(frequency=Count('id'))
            .order_by('-frequency')[:10]
        )

        return Response({
            "common_symptoms": symptoms,
            "detail": "These are the most frequent symptoms across all sick bay visits."
        })
