from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Student, MedicalFlag, StudentHistory
from .serializers import (
    StudentSerializer,
    MedicalFlagSerializer,
    StudentHistorySerializer
)
from .permissions import IsInstitutionAdminOrStaff, IsReadOnlyOrInstitutionStaff
from .filters import StudentFilter, MedicalFlagFilter
from .analytics import (
    get_class_level_distribution,
    get_stream_distribution,
    get_gender_breakdown_per_class,
    get_overcrowded_streams,
    get_empty_classes_and_streams,
    get_total_summary,
    get_enrollment_status_stats
)
from .ai import StudentAIAnalyzer


# ================================
# 🚸 Student Management
# ================================

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('institution', 'stream', 'class_level', 'assigned_class_teacher').all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsReadOnlyOrInstitutionStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ['first_name', 'last_name', 'admission_number', 'national_id']
    ordering_fields = ['first_name', 'last_name', 'date_joined', 'class_level__order']
    ordering = ['class_level__order', 'stream__order', 'last_name']

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(institution=user.institution)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def ai_insights(self, request, pk=None):
        student = self.get_object()
        analyzer = StudentAIAnalyzer(student)
        result = analyzer.run_full_analysis()
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def history(self, request, pk=None):
        student = self.get_object()
        history = StudentHistory.objects.filter(student=student)
        serializer = StudentHistorySerializer(history, many=True)
        return Response(serializer.data)


# ================================
# 🏥 Medical Alerts
# ================================

class MedicalFlagViewSet(viewsets.ModelViewSet):
    queryset = MedicalFlag.objects.select_related('student').all()
    serializer_class = MedicalFlagSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrStaff]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = MedicalFlagFilter
    search_fields = ['condition', 'student__first_name', 'student__last_name']

    def get_queryset(self):
        return self.queryset.filter(student__institution=self.request.user.institution)


# ================================
# 🧠 AI + 📊 Analytics APIs
# ================================

from rest_framework.views import APIView

class StudentAnalyticsDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrStaff]

    def get(self, request, *args, **kwargs):
        institution_id = request.user.institution_id
        return Response({
            "distribution_by_class": get_class_level_distribution(institution_id),
            "distribution_by_stream": get_stream_distribution(institution_id),
            "gender_breakdown": get_gender_breakdown_per_class(institution_id),
            "overcrowded_streams": get_overcrowded_streams(institution_id),
            "empty_classes_streams": get_empty_classes_and_streams(institution_id),
            "enrollment_stats": get_enrollment_status_stats(institution_id),
            "totals": get_total_summary(institution_id)
        }, status=status.HTTP_200_OK)
