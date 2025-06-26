from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
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


class CurriculumViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.all()
    serializer_class = CurriculumSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CurriculumSubjectViewSet(viewsets.ModelViewSet):
    queryset = CurriculumSubject.objects.all()
    serializer_class = CurriculumSubjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CurriculumSubjectFilter
    search_fields = ['curriculum__name', 'subject__name', 'class_level__name']


class SyllabusTopicViewSet(viewsets.ModelViewSet):
    queryset = SyllabusTopic.objects.all()
    serializer_class = SyllabusTopicSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SyllabusTopicFilter
    search_fields = ['title']


class SyllabusSubtopicViewSet(viewsets.ModelViewSet):
    queryset = SyllabusSubtopic.objects.all()
    serializer_class = SyllabusSubtopicSerializer
    permission_classes = [IsAdminOrReadOnly]


class LearningOutcomeViewSet(viewsets.ModelViewSet):
    queryset = LearningOutcome.objects.all()
    serializer_class = LearningOutcomeSerializer
    permission_classes = [IsAdminOrReadOnly]


class TeachingResourceViewSet(viewsets.ModelViewSet):
    queryset = TeachingResource.objects.all()
    serializer_class = TeachingResourceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'url']


class SyllabusProgressViewSet(viewsets.ModelViewSet):
    queryset = SyllabusProgress.objects.all()
    serializer_class = SyllabusProgressSerializer
    permission_classes = [IsTeacherOrAdminCanEdit]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SyllabusProgressFilter
    search_fields = ['topic__title', 'teacher__username']


class SyllabusVersionViewSet(viewsets.ModelViewSet):
    queryset = SyllabusVersion.objects.all()
    serializer_class = SyllabusVersionSerializer
    permission_classes = [IsSyllabusOwnerOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['version_notes']


class SyllabusAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SyllabusAuditLog.objects.all()
    serializer_class = SyllabusAuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['action', 'notes']
