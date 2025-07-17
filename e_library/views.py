from django.db.models import Q
from rest_framework import generics, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import ELibraryResource, ResourceViewLog
from .serializers import (
    ELibraryResourceSerializer,
    ELibraryResourceCreateSerializer,
    ResourceViewLogSerializer,
)
from .permissions import (
    IsInstitutionUploaderOrReadOnly,
    IsSchoolTeacherOrAdmin,
    IsStudentOfInstitution,
)
from .filters import ELibraryResourceFilter
from .analytics import ELibraryAnalytics
from .ai import ELibraryAIEngine


# -------------------------------
# List + Create Resources (Teacher/Admin)
# -------------------------------
class ELibraryResourceListCreateView(generics.ListCreateAPIView):
    queryset = ELibraryResource.objects.select_related(
        'uploader', 'institution', 'subject', 'class_level'
    ).prefetch_related('tags', 'recommended_for', 'versions')
    serializer_class = ELibraryResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ELibraryResourceFilter
    search_fields = ['title', 'description', 'subject__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(
            uploader=self.request.user,
            institution=self.request.user.institution
        )


# -------------------------------
# Detail View (Retrieve/Update/Delete)
# -------------------------------
class ELibraryResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ELibraryResource.objects.select_related(
        'uploader', 'institution', 'subject', 'class_level'
    ).prefetch_related('tags', 'recommended_for', 'versions')
    serializer_class = ELibraryResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionUploaderOrReadOnly]


# -------------------------------
# Public or Institutional Access (Students & General Users)
# -------------------------------
class PublicELibraryListView(generics.ListAPIView):
    serializer_class = ELibraryResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudentOfInstitution]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ELibraryResourceFilter
    search_fields = ['title', 'description', 'subject__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        institution_id = getattr(user, "institution_id", None)

        return ELibraryResource.objects.filter(
            Q(visibility='public') |
            Q(visibility='institution', institution_id=institution_id)
        ).select_related('subject', 'class_level')


# -------------------------------
# Track Resource Views (Usage Logging)
# -------------------------------
class ResourceViewLogCreateView(generics.CreateAPIView):
    serializer_class = ResourceViewLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -------------------------------
# AI Insights Endpoint (Internal or Admin Use)
# -------------------------------
class ELibraryAIInsightsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSchoolTeacherOrAdmin]

    def get(self, request):
        institution_id = getattr(request.user, "institution_id", None)
        popular = ELibraryAIEngine.analyze_resource_popularity(institution_id)
        trends = ELibraryAIEngine.analyze_usage_trends()
        return Response({
            "popular_resources": popular,
            "usage_trends": trends
        })


# -------------------------------
# Analytics Endpoint (ERP Dashboard)
# -------------------------------
class ELibraryAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSchoolTeacherOrAdmin]

    def get(self, request):
        institution_id = getattr(request.user, "institution_id", None)

        return Response({
            "most_viewed_resources": ELibraryAnalytics.most_viewed_resources(institution_id=institution_id),
            "active_users": ELibraryAnalytics.active_users(),
            "resource_type_distribution": ELibraryAnalytics.resource_type_distribution(institution_id=institution_id),
            "resource_visibility_stats": ELibraryAnalytics.resource_visibility_stats(institution_id=institution_id),
            "growth_over_time": ELibraryAnalytics.growth_over_time(interval='monthly', months=6),
            "most_used_categories": [
                {"id": cat.id, "name": cat.name, "count": cat.resource_count}
                for cat in ELibraryAnalytics.most_used_categories()
            ],
            "most_used_tags": [
                {"id": tag.id, "name": tag.name, "count": tag.usage}
                for tag in ELibraryAnalytics.most_used_tags()
            ],
            "versioned_resources_count": ELibraryAnalytics.versioned_resources_count(),
            "recently_added": [
                {"id": res.id, "title": res.title, "created_at": res.created_at}
                for res in ELibraryAnalytics.recently_added_resources()
            ]
        })


class MyELibraryResourcesView(generics.ListAPIView):
    serializer_class = ELibraryResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionUploaderOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ELibraryResourceFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, "profile", None)
        institution = getattr(profile, "institution", None)

        return ELibraryResource.objects.filter(
            Q(uploader=user) |
            Q(institution=institution, visibility__in=['institution', 'teachers', 'students', 'all'])
        ).select_related(
            'institution', 'uploader', 'subject', 'class_level'
        ).prefetch_related(
            'tags', 'category', 'recommended_for'
        )