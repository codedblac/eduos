from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import (
    AssessmentType, AssessmentTemplate, Assessment, Question, AnswerChoice,
    AssessmentSession, StudentAnswer, GradingRubric, MarkingScheme,
    AssessmentResult, Feedback, RetakePolicy
)
from .serializers import (
    AssessmentTypeSerializer, AssessmentTemplateSerializer, AssessmentSerializer,
    QuestionSerializer, AnswerChoiceSerializer, AssessmentSessionSerializer,
    StudentAnswerSerializer, GradingRubricSerializer, MarkingSchemeSerializer,
    AssessmentResultSerializer, FeedbackSerializer, RetakePolicySerializer
)
from .permissions import IsTeacherOrReadOnly, IsOwnerOrReadOnly
from .ai import (
    generate_assessment, generate_adaptive_assessment, predict_student_performance,
    detect_cheating_patterns, generate_remedial_assessment
)
from .analytics import (
    get_assessment_statistics, get_student_progress, get_question_performance
)


class AssessmentTypeViewSet(viewsets.ModelViewSet):
    queryset = AssessmentType.objects.all()
    serializer_class = AssessmentTypeSerializer
    permission_classes = [IsAuthenticated]


class AssessmentTemplateViewSet(viewsets.ModelViewSet):
    queryset = AssessmentTemplate.objects.all()
    serializer_class = AssessmentTemplateSerializer
    permission_classes = [IsAuthenticated]


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]

    @action(detail=True, methods=['post'])
    def auto_generate(self, request, pk=None):
        assessment = self.get_object()
        generated = generate_assessment(assessment)
        return Response(generated, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def adaptive_test(self, request, pk=None):
        assessment = self.get_object()
        student = request.user
        adaptive = generate_adaptive_assessment(assessment, student)
        return Response(adaptive, status=status.HTTP_200_OK)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class AnswerChoiceViewSet(viewsets.ModelViewSet):
    queryset = AnswerChoice.objects.all()
    serializer_class = AnswerChoiceSerializer
    permission_classes = [IsAuthenticated]


class AssessmentSessionViewSet(viewsets.ModelViewSet):
    queryset = AssessmentSession.objects.all()
    serializer_class = AssessmentSessionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class StudentAnswerViewSet(viewsets.ModelViewSet):
    queryset = StudentAnswer.objects.all()
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class GradingRubricViewSet(viewsets.ModelViewSet):
    queryset = GradingRubric.objects.all()
    serializer_class = GradingRubricSerializer
    permission_classes = [IsAuthenticated]


class MarkingSchemeViewSet(viewsets.ModelViewSet):
    queryset = MarkingScheme.objects.all()
    serializer_class = MarkingSchemeSerializer
    permission_classes = [IsAuthenticated]


class AssessmentResultViewSet(viewsets.ModelViewSet):
    queryset = AssessmentResult.objects.all()
    serializer_class = AssessmentResultSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def performance(self, request):
        student = request.user
        data = predict_student_performance(student)
        return Response(data)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class RetakePolicyViewSet(viewsets.ModelViewSet):
    queryset = RetakePolicy.objects.all()
    serializer_class = RetakePolicySerializer
    permission_classes = [IsAuthenticated]


# Analytics Views
from rest_framework.views import APIView

class AssessmentStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = get_assessment_statistics()
        return Response(stats)


class StudentProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        progress = get_student_progress(request.user)
        return Response(progress)


class QuestionPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        performance = get_question_performance()
        return Response(performance)


class CheatingDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        result = detect_cheating_patterns()
        return Response(result)


class RemedialAssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        result = generate_remedial_assessment(request.user)
        return Response(result)
