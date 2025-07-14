from rest_framework import viewsets, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Subject, SubjectClassLevel, SubjectTeacher,
    SubjectCategory, SubjectPrerequisite,
    SubjectAssessmentWeight, SubjectGradingScheme,
    SubjectResource, SubjectVersion
)

from .serializers import (
    SubjectSerializer, SubjectClassLevelSerializer, SubjectTeacherSerializer,
    SubjectCategorySerializer, SubjectPrerequisiteSerializer,
    SubjectAssessmentWeightSerializer, SubjectGradingSchemeSerializer,
    SubjectResourceSerializer, SubjectVersionSerializer
)

from .filters import (
    SubjectFilter, SubjectClassLevelFilter, SubjectTeacherFilter
)

from .permissions import (
    IsInstitutionAdminOrReadOnly, IsSubjectOwnerOrInstitutionAdmin
)

from .ai import SubjectAIEngine
from .analytics import SubjectAnalytics


# ---------------- Core ViewSets ----------------

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().select_related('category', 'institution')
    serializer_class = SubjectSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SubjectFilter
    search_fields = ['name', 'code', 'description']


class SubjectClassLevelViewSet(viewsets.ModelViewSet):
    queryset = SubjectClassLevel.objects.select_related('subject', 'class_level').all()
    serializer_class = SubjectClassLevelSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SubjectClassLevelFilter


class SubjectTeacherViewSet(viewsets.ModelViewSet):
    queryset = SubjectTeacher.objects.select_related('subject', 'teacher__user').all()
    serializer_class = SubjectTeacherSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SubjectTeacherFilter
    search_fields = ['teacher__user__first_name', 'teacher__user__last_name', 'subject__name']


class SubjectCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubjectCategory.objects.all()
    serializer_class = SubjectCategorySerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class SubjectPrerequisiteViewSet(viewsets.ModelViewSet):
    queryset = SubjectPrerequisite.objects.select_related('subject', 'prerequisite').all()
    serializer_class = SubjectPrerequisiteSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]


class SubjectAssessmentWeightViewSet(viewsets.ModelViewSet):
    queryset = SubjectAssessmentWeight.objects.select_related('subject').all()
    serializer_class = SubjectAssessmentWeightSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]


class SubjectGradingSchemeViewSet(viewsets.ModelViewSet):
    queryset = SubjectGradingScheme.objects.select_related('subject').all()
    serializer_class = SubjectGradingSchemeSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]


class SubjectResourceViewSet(viewsets.ModelViewSet):
    queryset = SubjectResource.objects.select_related('subject', 'uploaded_by').all()
    serializer_class = SubjectResourceSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'link']


class SubjectVersionViewSet(viewsets.ModelViewSet):
    queryset = SubjectVersion.objects.select_related('subject').all()
    serializer_class = SubjectVersionSerializer
    permission_classes = [IsInstitutionAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['version_number', 'changelog']


# ---------------- AI + Analytics ----------------

class SubjectAIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        institution_id = getattr(request.user, 'institution_id', None)
        if not institution_id:
            return Response({"error": "Institution not set for user"}, status=400)

        data = {
            "difficult_subjects": SubjectAIEngine.recommend_difficult_subjects_by_performance(institution_id),
            "subjects_with_coverage_gaps": SubjectAIEngine.detect_subjects_with_coverage_gaps(institution_id),
            "most_popular_subjects": SubjectAIEngine.get_subject_popularity(institution_id),
            "flagged_subjects_no_teachers": list(
                SubjectAIEngine.flag_subjects_without_teachers(institution_id).values('id', 'name')
            ),
        }
        return Response(data)


class SubjectAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        institution_id = getattr(request.user, 'institution_id', None)
        if not institution_id:
            return Response({"error": "Institution not set for user"}, status=400)

        data = {
            "teacher_distribution": SubjectAnalytics.teacher_engagement_metrics(institution_id),
            "coverage_percentages": SubjectAnalytics.institution_subject_coverage(institution_id),
            "popular_subjects": SubjectAnalytics.most_popular_subjects(institution_id),
            "low_performance_subjects": SubjectAnalytics.lowest_performing_subjects(institution_id),
            "teacher_subject_loads": SubjectAnalytics.teacher_subject_load_distribution(institution_id),
        }
        return Response(data)
