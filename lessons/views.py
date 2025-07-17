from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    LessonPlan, LessonSchedule, LessonSession,
    LessonAttachment, LessonScaffoldSuggestion
)
from .serializers import (
    LessonPlanSerializer, LessonScheduleSerializer, LessonSessionSerializer,
    LessonAttachmentSerializer, LessonScaffoldSuggestionSerializer
)
from .permissions import IsTeacherOrAdmin, IsLessonOwnerOrReadOnly
from .filters import LessonPlanFilter, LessonScheduleFilter, LessonSessionFilter
from .ai import LessonAI
from .analytics import LessonAnalytics


# ----------------------------
# Core ViewSets
# ----------------------------

class LessonPlanViewSet(viewsets.ModelViewSet):
    queryset = LessonPlan.objects.all()
    serializer_class = LessonPlanSerializer
    permission_classes = [IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LessonPlanFilter
    search_fields = ['title', 'objectives', 'resources']

    @action(detail=True, methods=['get'], url_path='ai-suggestions')
    def ai_suggestions(self, request, pk=None):
        lesson = self.get_object()
        suggestions = LessonAIEngine.suggest_for_lesson_plan(lesson)
        return Response(suggestions, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='coverage-alerts')
    def ai_coverage_alerts(self, request):
        alerts = LessonAI.detect_under_covered_topics()
        return Response(alerts, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='analytics-summary')
    def analytics_summary(self, request):
        stats = LessonAnalytics.planning_summary()
        return Response(stats, status=status.HTTP_200_OK)


class LessonScheduleViewSet(viewsets.ModelViewSet):
    queryset = LessonSchedule.objects.all()
    serializer_class = LessonScheduleSerializer
    permission_classes = [IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LessonScheduleFilter


class LessonSessionViewSet(viewsets.ModelViewSet):
    queryset = LessonSession.objects.all()
    serializer_class = LessonSessionSerializer
    permission_classes = [IsTeacherOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LessonSessionFilter

    @action(detail=False, methods=['get'], url_path='analytics')
    def session_analytics(self, request):
        stats = LessonAnalytics.session_analytics()
        return Response(stats, status=status.HTTP_200_OK)


class LessonAttachmentViewSet(viewsets.ModelViewSet):
    queryset = LessonAttachment.objects.all()
    serializer_class = LessonAttachmentSerializer
    permission_classes = [IsTeacherOrAdmin]


class LessonScaffoldSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LessonScaffoldSuggestion.objects.all()
    serializer_class = LessonScaffoldSuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]


# ----------------------------
# AI & Analytics APIViews (Optional but useful for frontend clarity)
# ----------------------------

class LessonAISuggestionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, lesson_plan_id):
        suggestions = LessonAI.suggest_for_lesson_plan_id(lesson_plan_id)
        return Response(suggestions)


class LessonCoverageAlertAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        alerts = LessonAI.detect_under_covered_topics()
        return Response(alerts)


class LessonAnalyticsSummaryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = LessonAnalytics.planning_summary()
        return Response(data)


class TeacherLessonAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, teacher_id):
        stats = LessonAnalytics.teacher_lesson_stats(teacher_id)
        return Response(stats)


class InstitutionLessonAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, institution_id):
        data = LessonAnalytics.institution_lesson_summary(institution_id)
        return Response(data)
