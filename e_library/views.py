from django.shortcuts import render

# Create your views here.
from django.db.models import Q

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import ELibraryResource
from .serializers import ELibraryResourceSerializer
from .permissions import IsTeacherOrAdmin, CanViewELibrary
from .filters import ELibraryResourceFilter
from .ai import generate_resource_insights

# -------------------------------
# List and Create Resources
# -------------------------------

class ELibraryResourceListCreateView(generics.ListCreateAPIView):
    queryset = ELibraryResource.objects.select_related('uploaded_by', 'institution', 'class_level')
    serializer_class = ELibraryResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ELibraryResourceFilter
    search_fields = ['title', 'subject', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user.teacher_profile, institution=self.request.user.institution)


# -------------------------------
# Retrieve, Update, Delete Resource
# -------------------------------

class ELibraryResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ELibraryResource.objects.select_related('uploaded_by', 'institution', 'class_level')
    serializer_class = ELibraryResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]


# -------------------------------
# Student/General Users: View Only
# -------------------------------

class PublicELibraryListView(generics.ListAPIView):
    serializer_class = ELibraryResourceSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewELibrary]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ELibraryResourceFilter
    search_fields = ['title', 'subject', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        institution_id = user.institution_id if hasattr(user, "institution_id") else None

        # Students see institutional + public resources
        return ELibraryResource.objects.filter(
            Q(visibility='public') |
            Q(institution_id=institution_id, visibility='institution')
        )


# -------------------------------
# AI-Powered Insights
# -------------------------------

class ELibraryInsightsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        resources = ELibraryResource.objects.all()
        data = generate_resource_insights(resources)
        return Response(data)
