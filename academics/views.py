from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend

from .models import AcademicYear, Term, AcademicEvent, HolidayBreak
from .serializers import (
    AcademicYearSerializer,
    TermSerializer,
    AcademicEventSerializer,
    HolidayBreakSerializer
)
from .permissions import IsAcademicAdminOrReadOnly, IsAcademicEditor
from .filters import (
    AcademicYearFilter,
    TermFilter,
    AcademicEventFilter,
    HolidayBreakFilter
)
from . import analytics, ai


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAcademicAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AcademicYearFilter

    @action(detail=False, methods=['get'], url_path='summary')
    def year_summary(self, request):
        data = analytics.academic_year_distribution()
        return Response(data)


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.select_related('academic_year')
    serializer_class = TermSerializer
    permission_classes = [IsAcademicAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TermFilter

    @action(detail=True, methods=['get'], url_path='ai-progress')
    def ai_progress(self, request, pk=None):
        term = self.get_object()
        progress = ai.AcademicAIEngine.predict_term_progress(term)
        return Response({"progress_percent": progress})

    @action(detail=True, methods=['get'], url_path='ai-summary')
    def ai_summary(self, request, pk=None):
        term = self.get_object()
        summary = ai.AcademicAIEngine.generate_term_summary(term)
        return Response(summary)

    @action(detail=True, methods=['get'], url_path='ai-conflicts')
    def ai_conflicts(self, request, pk=None):
        term = self.get_object()
        conflicts = ai.AcademicAIEngine.detect_term_conflicts(term)
        return Response({"conflicts": [str(c) for c in conflicts]})

    @action(detail=True, methods=['get'], url_path='ai-syllabus-gap')
    def ai_syllabus_gap(self, request, pk=None):
        term = self.get_object()
        gaps = ai.AcademicAIEngine.detect_syllabus_gap(term)
        return Response({"syllabus_gaps": gaps})

    @action(detail=True, methods=['get'], url_path='ai-schedule-suggestion')
    def schedule_suggestion(self, request, pk=None):
        term = self.get_object()
        message = ai.AcademicAIEngine.suggest_schedule_adjustments(term)
        return Response({"recommendation": message})

    @action(detail=False, methods=['get'], url_path='active')
    def active_terms(self, request):
        data = analytics.active_terms_summary()
        return Response(data)

    @action(detail=False, methods=['get'], url_path='term-stats')
    def term_statistics(self, request):
        stats = analytics.term_statistics()
        return Response(stats)


class AcademicEventViewSet(viewsets.ModelViewSet):
    queryset = AcademicEvent.objects.select_related('academic_year', 'term')
    serializer_class = AcademicEventSerializer
    permission_classes = [IsAcademicEditor]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AcademicEventFilter

    @action(detail=False, methods=['get'], url_path='distribution')
    def event_distribution(self, request):
        data = analytics.event_distribution_by_term()
        return Response(data)


class HolidayBreakViewSet(viewsets.ModelViewSet):
    queryset = HolidayBreak.objects.select_related('term')
    serializer_class = HolidayBreakSerializer
    permission_classes = [IsAcademicEditor]
    filter_backends = [DjangoFilterBackend]
    filterset_class = HolidayBreakFilter

    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        holidays = analytics.holiday_summary()
        return Response(holidays)
