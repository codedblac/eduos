from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, filters
from .models import GeneratedReport
from .serializers import GeneratedReportSerializer
from django_filters.rest_framework import DjangoFilterBackend


class GeneratedReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View reports for a user's institution.
    """
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['report_type', 'class_level', 'stream', 'term', 'year', 'access_level']
    ordering_fields = ['date_generated']
    search_fields = ['title', 'description']

    def get_queryset(self):
        institution = self.request.user.institution
        user = self.request.user

        # Role-based scoping: limit visibility by access_level
        qs = GeneratedReport.objects.filter(institution=institution)

        if not user.is_superuser and user.role != 'admin':
            if user.role == 'teacher':
                qs = qs.filter(access_level__in=['teacher', 'student', 'guardian'])
            elif user.role == 'guardian':
                qs = qs.filter(access_level__in=['guardian', 'student'])
            elif user.role == 'student':
                qs = qs.filter(access_level='student')
            else:
                qs = qs.none()

        return qs
