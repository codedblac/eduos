from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    ActivityCategory, Activity, StudentActivityParticipation,
    CoCurricularEvent, TalentProfile, Award, ActivitySchedule
)
from .serializers import (
    ActivityCategorySerializer, ActivitySerializer, StudentActivityParticipationSerializer,
    CoCurricularEventSerializer, TalentProfileSerializer, AwardSerializer,
    ActivityScheduleSerializer
)
from .permissions import IsAdminOrReadOnly, IsCoachOrReadOnly
from .filters import (
    ActivityCategoryFilter, ActivityFilter, StudentActivityParticipationFilter,
    CoCurricularEventFilter, TalentProfileFilter, AwardFilter, ActivityScheduleFilter
)
from .ai import TalentAIEngine
from .analytics import TalentAnalytics


class ActivityCategoryViewSet(viewsets.ModelViewSet):
    queryset = ActivityCategory.objects.all()
    serializer_class = ActivityCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivityCategoryFilter
    search_fields = ['name']


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivityFilter
    search_fields = ['name', 'description']


class StudentActivityParticipationViewSet(viewsets.ModelViewSet):
    queryset = StudentActivityParticipation.objects.all()
    serializer_class = StudentActivityParticipationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentActivityParticipationFilter
    search_fields = ['student__full_name', 'activity__name']


class CoCurricularEventViewSet(viewsets.ModelViewSet):
    queryset = CoCurricularEvent.objects.all()
    serializer_class = CoCurricularEventSerializer
    permission_classes = [IsAuthenticated, IsCoachOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CoCurricularEventFilter
    search_fields = ['name', 'description']


class TalentProfileViewSet(viewsets.ModelViewSet):
    queryset = TalentProfile.objects.all()
    serializer_class = TalentProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TalentProfileFilter
    search_fields = ['student__full_name', 'skills']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        data['ai_recommendations'] = TalentAIEngine.get_recommendations(instance.student)
        return Response(data)


class AwardViewSet(viewsets.ModelViewSet):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AwardFilter
    search_fields = ['title', 'description', 'level']


class ActivityScheduleViewSet(viewsets.ModelViewSet):
    queryset = ActivitySchedule.objects.all()
    serializer_class = ActivityScheduleSerializer
    permission_classes = [IsAuthenticated, IsCoachOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivityScheduleFilter
    search_fields = ['activity__name', 'description']


# AI & Analytics Endpoints
from rest_framework.decorators import api_view

@api_view(['GET'])
def recommended_activities(request, student_id):
    return Response({
        'recommendations': TalentAIEngine.get_recommendations_by_id(student_id)
    })


@api_view(['GET'])
def talent_analytics_overview(request):
    return Response(TalentAnalytics.get_overview())


@api_view(['GET'])
def participation_trends(request):
    return Response(TalentAnalytics.get_participation_trends())


@api_view(['GET'])
def underrepresented_groups(request):
    return Response(TalentAnalytics.get_underrepresented_groups())
