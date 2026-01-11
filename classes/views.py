from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from academics.models import AcademicYear

from .models import ClassLevel, Stream, StudentStreamEnrollment
from .serializers import ClassLevelSerializer, StreamSerializer
from .permissions import (
    IsInstitutionAdminOrStaff,
    IsReadOnlyOrInstitutionStaff,
    IsClassInstitutionMatch
)
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
from .ai import (
    suggest_balanced_allocation,
    generate_class_distribution_report
)


# ======================================================
# 🏫 CLASS LEVEL VIEWSET
# ======================================================
class ClassLevelViewSet(viewsets.ModelViewSet):
    serializer_class = ClassLevelSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsReadOnlyOrInstitutionStaff,
        IsClassInstitutionMatch
    ]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClassLevelFilter
    search_fields = ["name", "code"]
    ordering_fields = ["order", "name"]
    ordering = ["order", "name"]

    def get_queryset(self):
        return (
            ClassLevel.objects
            .select_related(
                "institution",
                "default_promotion_class",
                "class_teacher"
            )
            .filter(institution=self.request.user.institution)
        )

    def perform_create(self, serializer):
        # ✅ ClassLevel is NOT academic-year dependent
        serializer.save(
            institution=self.request.user.institution,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    # --------------------------------------------------
    # 🔽 Streams under a specific class level
    # --------------------------------------------------
    @action(detail=True, methods=["get"], url_path="streams")
    def streams(self, request, pk=None):
        class_level = self.get_object()

        streams = (
            Stream.objects
            .filter(class_level=class_level)
            .select_related(
                "class_level",
                "academic_year",
                "stream_teacher"
            )
            .annotate(
                # ✅ SAFE annotation name (no collision)
                _active_students=Count(
                    "enrollments_classes",
                    filter=Q(enrollments_classes__status="active"),
                    distinct=True
                )
            )
            .order_by("order", "name")
        )

        serializer = StreamSerializer(
            streams,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


# ======================================================
# 🧑‍🏫 STREAM VIEWSET
# ======================================================
class StreamViewSet(viewsets.ModelViewSet):
    serializer_class = StreamSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsReadOnlyOrInstitutionStaff,
        IsClassInstitutionMatch
    ]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StreamFilter
    search_fields = ["name", "code", "class_level__name"]
    ordering_fields = ["order", "name"]
    ordering = ["order", "name"]

    def get_queryset(self):
        return (
            Stream.objects
            .select_related(
                "class_level",
                "academic_year",
                "stream_teacher"
            )
            .filter(class_level__institution=self.request.user.institution)
            .annotate(
                # ✅ SAFE annotation
                _active_students=Count(
                    "enrollments_classes",
                    filter=Q(enrollments_classes__status="active"),
                    distinct=True
                )
            )
        )

    def perform_create(self, serializer):
        academic_year = (
            AcademicYear.objects
            .filter(
                institution=self.request.user.institution,
                is_current=True
            )
            .first()
        )

        if not academic_year:
            raise ValidationError("No active academic year found.")

        serializer.save(
            academic_year=academic_year,
            created_by=self.request.user,
            updated_by=self.request.user,
        )


# ======================================================
# 📊 CLASS ANALYTICS VIEW
# ======================================================
class ClassAnalyticsView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsInstitutionAdminOrStaff
    ]

    def get(self, request, *args, **kwargs):
        institution = request.user.institution

        academic_year = (
            AcademicYear.objects
            .filter(institution=institution, is_current=True)
            .first()
        )

        if not academic_year:
            return Response(
                {"detail": "No active academic year found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        institution_id = institution.id
        academic_year_id = academic_year.id

        data = {
            "distribution": get_class_level_distribution(
                institution_id,
                academic_year_id
            ),
            "streams": get_stream_distribution(
                institution_id,
                academic_year_id
            ),
            "gender_breakdown": get_gender_breakdown_per_class(
                institution_id,
                academic_year_id
            ),
            "overcrowded_streams": get_overcrowded_streams(
                institution_id,
                academic_year_id
            ),
            "empty_classes_streams": get_empty_classes_and_streams(
                institution_id,
                academic_year_id
            ),
            "enrollment_stats": get_enrollment_status_stats(
                institution_id,
                academic_year_id
            ),
            "totals": get_total_summary(
                institution_id,
                academic_year_id
            ),
        }

        return Response(data, status=status.HTTP_200_OK)


# ======================================================
# 🤖 AI / OPTIMIZATION VIEWS
# ======================================================
class StreamRedistributionSuggestionView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsInstitutionAdminOrStaff
    ]

    def get(self, request, *args, **kwargs):
        suggestions = suggest_balanced_allocation(
            institution=request.user.institution
        )
        return Response(suggestions, status=status.HTTP_200_OK)


class ClassDistributionReportView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsInstitutionAdminOrStaff
    ]

    def get(self, request, *args, **kwargs):
        report = generate_class_distribution_report(
            request.user.institution
        )
        return Response(report, status=status.HTTP_200_OK)
