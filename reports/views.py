# reports/views.py

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    GeneratedReport,
    ReportStudentPerformance,
    ReportSubjectBreakdown
)
from .serializers import (
    GeneratedReportSerializer,
    ReportStudentPerformanceSerializer,
    ReportSubjectBreakdownSerializer
)
from .permissions import (
    IsReportCreatorOrAdmin,
    CanViewReportByAccessLevel,
    IsInstitutionMember,
    CanGenerateReports
)
from .filters import GeneratedReportFilter
from .tasks import (
    generate_academic_report_task,
    run_ai_analysis_on_report,
    export_report_as_pdf,
    export_report_as_excel,
    notify_top_performers
)
from .ai import subject_failure_alerts
from .analytics import (
    class_average_per_term,
    stream_top_performers,
    grade_distribution_chart,
    subject_difficulty_index,
    most_improved_students
)


# ------------------------------------
# Report CRUD Views
# ------------------------------------

class GeneratedReportListCreateView(generics.ListCreateAPIView):
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = GeneratedReportFilter
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        user = self.request.user
        return GeneratedReport.objects.filter(institution=user.institution)

    def perform_create(self, serializer):
        serializer.save(
            generated_by=self.request.user,
            institution=self.request.user.institution
        )


class GeneratedReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsReportCreatorOrAdmin, IsInstitutionMember]


# ------------------------------------
# Report Export Views
# ------------------------------------

class ExportReportPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanViewReportByAccessLevel]

    def get(self, request, pk):
        report = get_object_or_404(GeneratedReport, pk=pk)
        result = export_report_as_pdf(report.id)
        if result:
            return FileResponse(open(result['file_path'], 'rb'), content_type='application/pdf')
        return Response({'detail': 'PDF export failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExportReportExcelView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanViewReportByAccessLevel]

    def get(self, request, pk):
        report = get_object_or_404(GeneratedReport, pk=pk)
        result = export_report_as_excel(report.id)
        if result:
            return FileResponse(open(result['file_path'], 'rb'), content_type='application/vnd.ms-excel')
        return Response({'detail': 'Excel export failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------------------------
# Report Task Triggers
# ------------------------------------

class TriggerReportGenerationView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanGenerateReports]

    def post(self, request):
        data = request.data
        term = data.get("term")
        year = data.get("year")
        class_level_id = data.get("class_level_id")
        stream_id = data.get("stream_id")
        institution_id = data.get("institution_id")

        task = generate_academic_report_task.delay(
            term, year, class_level_id, stream_id, institution_id, request.user.id
        )
        return Response({"status": "task_submitted", "task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class TriggerAIInsightsView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanGenerateReports]

    def post(self, request, pk):
        task = run_ai_analysis_on_report.delay(pk)
        return Response({"status": "ai_analysis_started", "task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class NotifyTopPerformersView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanGenerateReports]

    def post(self, request, pk):
        top_n = int(request.data.get("top_n", 5))
        task = notify_top_performers.delay(pk, top_n)
        return Response({"status": "notification_triggered", "task_id": task.id}, status=status.HTTP_202_ACCEPTED)


# ------------------------------------
# Performance Views
# ------------------------------------

class ReportStudentPerformanceView(generics.ListAPIView):
    serializer_class = ReportStudentPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewReportByAccessLevel]

    def get_queryset(self):
        report_id = self.kwargs.get('report_id')
        return ReportStudentPerformance.objects.filter(report_id=report_id)


class ReportSubjectBreakdownView(generics.ListAPIView):
    serializer_class = ReportSubjectBreakdownSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewReportByAccessLevel]

    def get_queryset(self):
        report_id = self.kwargs.get('report_id')
        return ReportSubjectBreakdown.objects.filter(report_id=report_id)


# ------------------------------------
# Analytics Views
# ------------------------------------

class ClassPerformanceTrendsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, institution_id, class_level_id, stream_id=None):
        data = class_average_per_term(institution_id, class_level_id, stream_id)
        return Response(data)


class SubjectDifficultyAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, institution_id):
        data = subject_difficulty_index(institution_id)
        return Response(data)


class StreamTopPerformersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, report_id):
        top_students = stream_top_performers(report_id)
        data = ReportStudentPerformanceSerializer(top_students, many=True).data
        return Response(data)


class GradeDistributionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, report_id):
        chart = grade_distribution_chart(report_id)
        return Response(chart)


class MostImprovedStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        student_ids = request.data.get("student_ids", [])
        institution_id = request.data.get("institution_id")
        results = most_improved_students(institution_id, student_ids)
        return Response(results)


class SubjectFailureAlertsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, report_id):
        report = get_object_or_404(GeneratedReport, id=report_id)
        alerts = subject_failure_alerts(report)
        return Response(alerts)
