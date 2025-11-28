from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import ClassLevel, Stream
from .serializers import ClassLevelSerializer, StreamSerializer
from .permissions import IsInstitutionAdminOrStaff, IsReadOnlyOrInstitutionStaff, IsClassInstitutionMatch
from .filters import ClassLevelFilter, StreamFilter
from .analytics import (
    get_class_level_distribution,
    get_stream_distribution,
    get_gender_breakdown_per_class,
    get_overcrowded_streams,
    get_empty_classes_and_streams,
    get_total_summary,
    get_enrollment_status_stats
)
from .ai import suggest_balanced_allocation, generate_class_distribution_report


class ClassLevelViewSet(viewsets.ModelViewSet):
    queryset = ClassLevel.objects.select_related('institution', 'default_promotion_class').all()
    serializer_class = ClassLevelSerializer
    permission_classes = [permissions.IsAuthenticated, IsReadOnlyOrInstitutionStaff, IsClassInstitutionMatch]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClassLevelFilter
    search_fields = ['name', 'code']
    ordering_fields = ['order', 'name']
    ordering = ['order', 'name']


class StreamViewSet(viewsets.ModelViewSet):
    queryset = Stream.objects.select_related(
        'class_level', 'academic_year', 'institution', 'class_teacher'
    ).all()
    serializer_class = StreamSerializer
    permission_classes = [permissions.IsAuthenticated, IsReadOnlyOrInstitutionStaff, IsClassInstitutionMatch]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StreamFilter
    search_fields = ['name', 'code', 'class_level__name']
    ordering_fields = ['order', 'name']
    ordering = ['order', 'name']


# =============================
# 📊 Analytics + AI ViewSet
# =============================

from rest_framework.views import APIView

class ClassAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrStaff]

    def get(self, request, *args, **kwargs):
        institution_id = request.user.institution_id
        data = {
            "distribution": get_class_level_distribution(institution_id),
            "streams": get_stream_distribution(institution_id),
            "gender_breakdown": get_gender_breakdown_per_class(institution_id),
            "overcrowded_streams": get_overcrowded_streams(institution_id),
            "empty_classes_streams": get_empty_classes_and_streams(institution_id),
            "enrollment_stats": get_enrollment_status_stats(institution_id),
            "totals": get_total_summary(institution_id)
        }
        return Response(data, status=status.HTTP_200_OK)


class StreamRedistributionSuggestionView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrStaff]

    def get(self, request, *args, **kwargs):
        institution_id = request.user.institution_id
        suggestions = suggest_balanced_allocation(institution=request.user.institution)
        return Response(suggestions, status=status.HTTP_200_OK)


class ClassDistributionReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrStaff]

    def get(self, request, *args, **kwargs):
        institution = request.user.institution
        report = generate_class_distribution_report(institution)
        return Response(report, status=status.HTTP_200_OK)
