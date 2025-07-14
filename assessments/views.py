# assessments/views.py

from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Count

from assessments.models import (
    AssessmentType, AssessmentTemplate, Assessment, Question, AnswerChoice,
    AssessmentSession, StudentAnswer, MarkingScheme, GradingRubric, Feedback,
    RetakePolicy, AssessmentGroup, AssessmentWeight, AssessmentLock,
    AssessmentVisibility, PerformanceTrend, CodeTestCase
)
from assessments.serializers import (
    AssessmentTypeSerializer, AssessmentTemplateSerializer, AssessmentSerializer,
    QuestionSerializer, AnswerChoiceSerializer, AssessmentSessionSerializer,
    StudentAnswerSerializer, MarkingSchemeSerializer, GradingRubricSerializer,
    FeedbackSerializer, RetakePolicySerializer, AssessmentGroupSerializer,
    AssessmentWeightSerializer, AssessmentLockSerializer, AssessmentVisibilitySerializer,
    PerformanceTrendSerializer, CodeTestCaseSerializer
)
from assessments.analytics import *
from assessments.ai import AssessmentAIEngine
from students.models import Student


# ---------------------- Basic Model ViewSets ----------------------

class AssessmentTypeViewSet(viewsets.ModelViewSet):
    queryset = AssessmentType.objects.all()
    serializer_class = AssessmentTypeSerializer


class AssessmentTemplateViewSet(viewsets.ModelViewSet):
    queryset = AssessmentTemplate.objects.all()
    serializer_class = AssessmentTemplateSerializer


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['scheduled_date', 'total_marks']

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        assessment = self.get_object()
        lock, created = AssessmentLock.objects.get_or_create(assessment=assessment)
        lock.locked = True
        lock.locked_at = timezone.now()
        lock.save()
        return Response({'status': 'Assessment locked'})

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        assessment = self.get_object()
        assessment.is_published = True
        assessment.save()
        return Response({'status': 'Assessment published'})


class AssessmentGroupViewSet(viewsets.ModelViewSet):
    queryset = AssessmentGroup.objects.all()
    serializer_class = AssessmentGroupSerializer


class AssessmentWeightViewSet(viewsets.ModelViewSet):
    queryset = AssessmentWeight.objects.all()
    serializer_class = AssessmentWeightSerializer


class AssessmentSessionViewSet(viewsets.ModelViewSet):
    queryset = AssessmentSession.objects.select_related('student', 'assessment')
    serializer_class = AssessmentSessionSerializer


class StudentAnswerViewSet(viewsets.ModelViewSet):
    queryset = StudentAnswer.objects.select_related('question', 'session')
    serializer_class = StudentAnswerSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('assessment', 'topic')
    serializer_class = QuestionSerializer


class AnswerChoiceViewSet(viewsets.ModelViewSet):
    queryset = AnswerChoice.objects.select_related('question')
    serializer_class = AnswerChoiceSerializer


class MarkingSchemeViewSet(viewsets.ModelViewSet):
    queryset = MarkingScheme.objects.select_related('question')
    serializer_class = MarkingSchemeSerializer


class GradingRubricViewSet(viewsets.ModelViewSet):
    queryset = GradingRubric.objects.select_related('question')
    serializer_class = GradingRubricSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.select_related('session')
    serializer_class = FeedbackSerializer


class RetakePolicyViewSet(viewsets.ModelViewSet):
    queryset = RetakePolicy.objects.select_related('assessment')
    serializer_class = RetakePolicySerializer


class AssessmentLockViewSet(viewsets.ModelViewSet):
    queryset = AssessmentLock.objects.select_related('assessment')
    serializer_class = AssessmentLockSerializer


class AssessmentVisibilityViewSet(viewsets.ModelViewSet):
    queryset = AssessmentVisibility.objects.select_related('session')
    serializer_class = AssessmentVisibilitySerializer


class PerformanceTrendViewSet(viewsets.ModelViewSet):
    queryset = PerformanceTrend.objects.select_related('student', 'subject')
    serializer_class = PerformanceTrendSerializer


class CodeTestCaseViewSet(viewsets.ModelViewSet):
    queryset = CodeTestCase.objects.select_related('question')
    serializer_class = CodeTestCaseSerializer


# ---------------------- Analytics ----------------------

class InstitutionPerformanceView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        institution = request.user.institution
        data = overall_performance_summary(institution)
        return Response(data)


class StudentTrendView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        student = request.user.student
        data = student_performance_trend(student)
        return Response(data)


class HeatmapView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        student = request.user.student
        data = topic_mastery_heatmap(student)
        return Response(data)


class ParticipationRateView(generics.GenericAPIView):
    def get(self, request, assessment_id, *args, **kwargs):
        assessment = Assessment.objects.get(id=assessment_id)
        data = assessment_participation_rate(assessment)
        return Response(data)


# ---------------------- AI Utilities ----------------------

class AdaptiveAssessmentView(generics.GenericAPIView):
    def get(self, request, subject_id):
        student = request.user.student
        subject = Subject.objects.get(id=subject_id)
        questions = AssessmentAIEngine.generate_adaptive_assessment(
            student=student,
            subject=subject,
            class_level=student.class_level,
            term=student.current_term,
        )
        return Response(QuestionSerializer(questions, many=True).data)


class PredictedScoreView(generics.GenericAPIView):
    def get(self, request, subject_id):
        student = request.user.student
        subject = Subject.objects.get(id=subject_id)
        score = AssessmentAIEngine.predict_student_score(student, subject)
        return Response({"predicted_score": score})
