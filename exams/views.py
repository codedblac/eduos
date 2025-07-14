# exams/views.py

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.http import FileResponse
from exams.render import (
    generate_latex_exam,
    render_exam_to_pdf,
    render_marking_scheme
)
from exams.render import render_exam_to_pdf, generate_latex_exam
from django.http import HttpResponse
from rest_framework import viewsets, status, parsers
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    Exam, ExamSubject, ExamResult, StudentScore,
    GradeBoundary, ExamInsight, ExamPrediction
)
from .serializers import (
    ExamSerializer, ExamSubjectSerializer, ExamResultSerializer,
    StudentScoreSerializer, GradeBoundarySerializer,
    ExamInsightSerializer, ExamPredictionSerializer
)
# from .permissions import IsExamManagerOrReadOnly
from . import ai as ai_engine, analytics, grading_engine, render

from .utils import (
    calculate_exam_statistics, generate_student_ranking,
    bulk_assign_grades_and_positions, get_student_exam_summary,
    normalize_score, generate_exam_slug, format_exam_label
)

from .ocr import extract_text_from_image, extract_text_from_pdf, extract_exam_metadata


class RenderExamPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        include_answers = request.query_params.get("answers", "false").lower() == "true"
        randomize = request.query_params.get("random", "false").lower() == "true"
        exam = get_object_or_404(Exam, pk=exam_id)
        try:
            pdf_path = render.render_exam_to_pdf(exam, include_answers=include_answers, randomize=randomize)
            return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OCRExtractView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser]

    def post(self, request, filetype):
        file = request.FILES.get(filetype)
        if not file:
            return Response({"error": f"{filetype} file is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Temp save
        from tempfile import NamedTemporaryFile
        temp = NamedTemporaryFile(delete=False, suffix=f".{filetype}")
        temp.write(file.read())
        temp.flush()
        temp.close()

        try:
            text = extract_text_from_pdf(temp.name) if filetype == 'pdf' else extract_text_from_image(temp.name)
            metadata = extract_exam_metadata(text)
            return Response({"text": text, "metadata": metadata})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            import os
            os.unlink(temp.name)


class ExamStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        stats = calculate_exam_statistics(exam)
        return Response(stats)


class BulkActionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exam_id, action):
        exam = get_object_or_404(Exam, id=exam_id)
        if action == 'assign-grades':
            bulk_assign_grades_and_positions(exam)
        elif action == 'generate-ranking':
            generate_student_ranking(exam)
        else:
            return Response({"error": "Unknown action"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": f"{action} successful"})


class StudentExamSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id, student_id):
        exam = get_object_or_404(Exam, id=exam_id)
        summary = get_student_exam_summary(get_object_or_404(StudentScore._meta.get_field('student').related_model, id=student_id), exam)
        return Response(summary)


class UtilityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, util):
        if util == 'normalize-score':
            raw_score = float(request.data.get('raw_score', 0))
            max_raw = float(request.data.get('max_raw', 0))
            target = float(request.data.get('target_max', 100))
            return Response({"normalized_score": normalize_score(raw_score, max_raw, target)})
        elif util == 'generate-slug':
            name = request.data.get('name')
            if not name:
                return Response({"error": "Missing 'name'."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"slug": generate_exam_slug(name)})
        else:
            return Response({"error": "Unknown utility"}, status=status.HTTP_400_BAD_REQUEST)


class FormatExamLabelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        return Response({"label": format_exam_label(exam)})


# --- ViewSets ---

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        exam = self.get_object()
        grading_engine.grade_all_results_for_exam(exam)
        return Response({"status": "Exam graded successfully"})

    @action(detail=True, methods=['get'])
    def insights(self, request, pk=None):
        insights = analytics.overall_exam_performance(exam := self.get_object())
        return Response(insights)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        exam = self.get_object()
        pdf_path = render.render_exam_to_pdf(exam)
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')


class ExamSubjectViewSet(viewsets.ModelViewSet):
    queryset = ExamSubject.objects.all()
    serializer_class = ExamSubjectSerializer
    permission_classes = [IsAuthenticated]


class StudentScoreViewSet(viewsets.ModelViewSet):
    queryset = StudentScore.objects.all()
    serializer_class = StudentScoreSerializer
    permission_classes = [IsAuthenticated]


class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def student_report(self, request):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response({"error": "student_id required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(analytics.individual_student_report(get_object_or_404(StudentScore._meta.get_field('student').related_model, id=student_id)))


class GradeBoundaryViewSet(viewsets.ModelViewSet):
    queryset = GradeBoundary.objects.all()
    serializer_class = GradeBoundarySerializer
    permission_classes = [IsAuthenticated]


class ExamInsightViewSet(viewsets.ModelViewSet):
    queryset = ExamInsight.objects.all()
    serializer_class = ExamInsightSerializer
    permission_classes = [IsAuthenticated]


class ExamPredictionViewSet(viewsets.ModelViewSet):
    queryset = ExamPrediction.objects.all()
    serializer_class = ExamPredictionSerializer
    permission_classes = [IsAuthenticated]




class RenderExamLaTeXView(APIView):
    def get(self, request, exam_id):
        try:
            exam = Exam.objects.get(id=exam_id)
            latex = generate_latex_exam(exam)
            return Response({"latex": latex}, status=status.HTTP_200_OK)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RenderExamPDFView(APIView):
    def get(self, request, exam_id):
        try:
            exam = Exam.objects.get(id=exam_id)
            pdf_path = render_exam_to_pdf(exam)
            with open(pdf_path, 'rb') as pdf_file:
                return HttpResponse(pdf_file.read(), content_type='application/pdf')
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RenderMarkingSchemeView(APIView):
    def get(self, request, exam_id):
        try:
            exam = Exam.objects.get(id=exam_id)
            latex = render_marking_scheme(exam)
            return Response({"marking_scheme_latex": latex}, status=status.HTTP_200_OK)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)