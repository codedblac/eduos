from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from lessons.models import LessonPlan, LessonSession, LessonSchedule, LessonAttachment
from lessons.serializers import (
    LessonPlanSerializer, LessonSessionSerializer, 
    LessonScheduleSerializer, LessonAttachmentSerializer
)
from lessons.permissions import IsTeacherOrReadOnly
from lessons.filters import LessonPlanFilter, LessonSessionFilter, LessonScheduleFilter
from lessons.analytics import (
    get_teacher_workload, get_lesson_coverage_report, 
    get_missed_lessons_stats, get_average_lesson_duration
)
from lessons.ai import generate_lesson_plan_suggestions, predict_uncovered_topics


class LessonPlanViewSet(viewsets.ModelViewSet):
    queryset = LessonPlan.objects.all()
    serializer_class = LessonPlanSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LessonPlanFilter

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        suggestions = generate_lesson_plan_suggestions()
        return Response(suggestions)

    @action(detail=False, methods=['get'])
    def coverage_report(self, request):
        term_id = request.query_params.get("term")
        if not term_id:
            return Response({"error": "Term parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        report = get_lesson_coverage_report(term_id)
        return Response(report)


class LessonSessionViewSet(viewsets.ModelViewSet):
    queryset = LessonSession.objects.all()
    serializer_class = LessonSessionSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LessonSessionFilter


class LessonScheduleViewSet(viewsets.ModelViewSet):
    queryset = LessonSchedule.objects.all()
    serializer_class = LessonScheduleSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LessonScheduleFilter


class LessonAttachmentViewSet(viewsets.ModelViewSet):
    queryset = LessonAttachment.objects.all()
    serializer_class = LessonAttachmentSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]


class LessonAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        data = {
            "teacher_workload": get_teacher_workload(request.user),
            "coverage_stats": get_lesson_coverage_report(request.query_params.get("term")),
            "missed_lessons": get_missed_lessons_stats(),
            "average_duration": get_average_lesson_duration(),
            "syllabus_risks": predict_uncovered_topics(),
        }
        return Response(data)
