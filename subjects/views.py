from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from .models import Subject, SubjectClassLevel, SubjectTeacher
from .serializers import SubjectSerializer, SubjectClassLevelSerializer, SubjectTeacherSerializer
from .filters import SubjectFilter
from .permissions import CanManageSubjects
from django_filters.rest_framework import DjangoFilterBackend


class SubjectListCreateView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageSubjects]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SubjectFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Subject.objects.all()
        return Subject.objects.filter(institution=user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class SubjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageSubjects]


class SubjectClassLevelListCreateView(generics.ListCreateAPIView):
    queryset = SubjectClassLevel.objects.all()
    serializer_class = SubjectClassLevelSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageSubjects]


class SubjectTeacherListCreateView(generics.ListCreateAPIView):
    queryset = SubjectTeacher.objects.all()
    serializer_class = SubjectTeacherSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageSubjects]
