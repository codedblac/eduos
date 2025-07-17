from rest_framework import viewsets, generics, filters, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from collections import Counter
from students.serializers import StudentSerializer 
from exams.models import StudentScore, ExamSubject
from subjects.models import Subject
from subjects.serializers import SubjectSerializer


from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from .models import AssessmentResult
from students.models import Student

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

from assessments.analytics import (
    get_overall_performance_summary,
    get_student_performance_trend,
    get_subject_coverage_analysis,
    get_flagged_students,
    get_topic_mastery_heatmap,
    get_assessment_participation_rate
)

from assessments.ai import (
    generate_adaptive_assessment,
    predict_student_score,
    recommend_remedial_assessment,
    get_underrepresented_topics,
    suggest_questions_for_topic
)

from students.models import Student
from subjects.models import Subject


# ---------------------- Model ViewSets ----------------------

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
        lock, _ = AssessmentLock.objects.get_or_create(assessment=assessment)
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

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def overall_performance_summary_view(request):
    data = get_overall_performance_summary(request.user.institution)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_performance_trend_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    trend = get_student_performance_trend(student)
    return Response(trend)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subject_coverage_analysis_view(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    coverage = get_subject_coverage_analysis(subject)
    return Response(coverage)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def flagged_students_view(request):
    flagged = get_flagged_students(request.user.institution)
    return Response(flagged)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def topic_mastery_heatmap_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    heatmap = get_topic_mastery_heatmap(student)
    return Response(heatmap)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def assessment_participation_rate_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    data = get_assessment_participation_rate(assessment)
    return Response(data)


# ---------------------- AI Views ----------------------

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generate_adaptive_assessment_view(request, student_id, subject_id, class_level_id, term_id):
    data = generate_adaptive_assessment(student_id, subject_id, class_level_id, term_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def predict_student_score_view(request, student_id, subject_id):
    score = predict_student_score(student_id, subject_id)
    return Response({'predicted_score': score})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recommend_remedial_assessment_view(request, student_id, subject_id):
    data = recommend_remedial_assessment(student_id, subject_id)
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def underrepresented_topics_view(request, subject_id):
    topics = get_underrepresented_topics(subject_id)
    return Response({'topics': topics})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def suggest_questions_for_topic_view(request, topic_id):
    questions = suggest_questions_for_topic(topic_id)
    return Response({'questions': questions})

@api_view(['POST'])
def lock_assessment(request, pk):
    try:
        assessment = Assessment.objects.get(pk=pk)
        assessment.is_locked = True
        assessment.save()
        return Response({'detail': 'Assessment locked successfully'}, status=status.HTTP_200_OK)
    except Assessment.DoesNotExist:
        return Response({'detail': 'Assessment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    
@api_view(['POST'])
def publish_assessment(request, pk):
    try:
        assessment = Assessment.objects.get(pk=pk)
        assessment.is_published = True
        assessment.save()
        return Response({'detail': 'Assessment published successfully'}, status=status.HTTP_200_OK)
    except Assessment.DoesNotExist:
        return Response({'detail': 'Assessment not found'}, status=status.HTTP_404_NOT_FOUND) 
    
    
@api_view(['GET'])
def assessment_type_distribution_view(request):
    type_counts = Assessment.objects.values_list('type', flat=True)
    distribution = dict(Counter(type_counts))
    return Response({
        'type_distribution': distribution
    }, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
def top_performing_students_view(request):
    limit = int(request.query_params.get('limit', 10))  # Optional: ?limit=5
    top_scores = (
        AssessmentResult.objects
        .values('student')
        .annotate(avg_score=Avg('score'))
        .order_by('-avg_score')[:limit]
    )

    student_ids = [entry['student'] for entry in top_scores]
    students = Student.objects.filter(id__in=student_ids)

    # Map student to avg_score
    score_map = {entry['student']: entry['avg_score'] for entry in top_scores}
    data = []
    for student in students:
        serialized = StudentSerializer(student).data
        serialized['average_score'] = round(score_map[student.id], 2)
        data.append(serialized)

    return Response({'top_performers': data}, status=status.HTTP_200_OK)



@api_view(['GET'])
def subject_difficulty_ranking_view(request):
    # Compute average score per subject
    avg_scores = (
        AssessmentResult.objects
        .values('exam_subject__subject')
        .annotate(avg_score=Avg('score'))
        .order_by('avg_score')  # ascending: low score = more difficult
    )

    subject_ids = [entry['exam_subject__subject'] for entry in avg_scores]
    subjects = Subject.objects.filter(id__in=subject_ids)

    score_map = {entry['exam_subject__subject']: entry['avg_score'] for entry in avg_scores}
    ranked_subjects = []
    for subject in subjects:
        serialized = SubjectSerializer(subject).data
        serialized['average_score'] = round(score_map[subject.id], 2)
        ranked_subjects.append(serialized)

    return Response({'difficulty_ranking': ranked_subjects}, status=status.HTTP_200_OK)