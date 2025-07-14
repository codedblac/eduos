from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import (
    Curriculum, CurriculumSubject, SyllabusTopic, SyllabusSubtopic,
    LearningOutcome, TeachingResource, SyllabusProgress,
    SyllabusVersion, SyllabusAuditLog
)
from .serializers import (
    CurriculumSerializer, CurriculumSubjectSerializer, SyllabusTopicSerializer,
    SyllabusSubtopicSerializer, LearningOutcomeSerializer, TeachingResourceSerializer,
    SyllabusProgressSerializer, SyllabusVersionSerializer, SyllabusAuditLogSerializer
)
from .permissions import (
    IsAdminOrReadOnly, IsTeacherOrAdminCanEdit, IsSyllabusOwnerOrAdmin
)
from .filters import (
    SyllabusTopicFilter, SyllabusProgressFilter, CurriculumSubjectFilter
)
from .analytics import SyllabusAnalytics
from .ai import SyllabusAI


class CurriculumViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.all()
    serializer_class = CurriculumSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['institution', 'is_active']


class CurriculumSubjectViewSet(viewsets.ModelViewSet):
    queryset = CurriculumSubject.objects.select_related('curriculum', 'subject', 'class_level', 'term').all()
    serializer_class = CurriculumSubjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CurriculumSubjectFilter
    search_fields = ['curriculum__name', 'subject__name', 'class_level__name']


class SyllabusTopicViewSet(viewsets.ModelViewSet):
    queryset = SyllabusTopic.objects.prefetch_related('subtopics', 'outcomes').all()
    serializer_class = SyllabusTopicSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SyllabusTopicFilter
    search_fields = ['title']
    ordering_fields = ['order', 'estimated_duration_minutes']
    ordering = ['order']

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def suggestions(self, request, pk=None):
        topic = self.get_object()
        suggestions = SyllabusAI.suggest_related_topics(topic.title, topic.curriculum_subject.subject.id)
        return Response(SyllabusTopicSerializer(suggestions, many=True).data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def recommended_resources(self, request, pk=None):
        resources = SyllabusAI.recommend_resources_for_topic(pk)
        return Response(TeachingResourceSerializer(resources, many=True).data)


class SyllabusSubtopicViewSet(viewsets.ModelViewSet):
    queryset = SyllabusSubtopic.objects.all()
    serializer_class = SyllabusSubtopicSerializer
    permission_classes = [IsAdminOrReadOnly]


class LearningOutcomeViewSet(viewsets.ModelViewSet):
    queryset = LearningOutcome.objects.all()
    serializer_class = LearningOutcomeSerializer
    permission_classes = [IsAdminOrReadOnly]


class TeachingResourceViewSet(viewsets.ModelViewSet):
    queryset = TeachingResource.objects.select_related('uploaded_by').all()
    serializer_class = TeachingResourceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'url']
    filterset_fields = ['type', 'uploaded_by']


class SyllabusProgressViewSet(viewsets.ModelViewSet):
    queryset = SyllabusProgress.objects.select_related('topic', 'teacher').all()
    serializer_class = SyllabusProgressSerializer
    permission_classes = [IsTeacherOrAdminCanEdit]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SyllabusProgressFilter
    search_fields = ['topic__title', 'teacher__username']
    ordering_fields = ['coverage_date']
    ordering = ['-coverage_date']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_progress(self, request):
        """
        Returns logged-in teacher’s syllabus progress.
        """
        qs = self.queryset.filter(teacher=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def slow_topics(self, request):
        """
        Admins only: Flag slow-covered topics.
        """
        flagged = SyllabusAI.flag_slow_topics()
        serializer = self.get_serializer(flagged, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def coverage_stats(self, request):
        """
        Returns summary coverage for the logged-in teacher.
        """
        stats = SyllabusAnalytics.syllabus_coverage_by_teacher(request.user.id)
        return Response(stats)


class SyllabusVersionViewSet(viewsets.ModelViewSet):
    queryset = SyllabusVersion.objects.select_related('curriculum_subject', 'created_by').all()
    serializer_class = SyllabusVersionSerializer
    permission_classes = [IsSyllabusOwnerOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['version_number', 'change_log']


class SyllabusAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SyllabusAuditLog.objects.select_related('user', 'curriculum_subject', 'topic').all()
    serializer_class = SyllabusAuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['action', 'notes']
    filterset_fields = ['user', 'curriculum_subject', 'action']
