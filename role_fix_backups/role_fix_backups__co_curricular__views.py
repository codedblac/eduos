from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    ActivityCategory,
    Activity,
    StudentActivityParticipation,
    ActivityEvent,
    StudentAward,
    ActivitySession,
    StudentProfile,
    CoachFeedback,
    TalentRecommendation
)
from .serializers import (
    CoCurricularCategorySerializer,
    ActivitySerializer,
    StudentActivitySerializer,
    ActivityEventSerializer,
    AwardSerializer,
    # ActivityScheduleSerializer,
    StudentProfileSerializer,
    CoachFeedbackSerializer,
    TalentScoutingSerializer
)
from .permissions import IsAdminOrActivityManager, IsCoachOrReadOnly
from .filters import (
    ActivityCategoryFilter,
    ActivityFilter,
    StudentProfileFilter,
    StudentActivityParticipationFilter,
    ActivityEventFilter,
    StudentAwardFilter,
    CoachFeedbackFilter
)
from .ai import talent_ai
from .analytics import (
    get_participation_summary,
    get_award_statistics,
    get_student_talent_distribution,
    get_activity_popularity,
    detect_low_participation_students,
    detect_gender_disparity_by_activity,
    activity_trends_over_time,
    coach_performance_summary
)


class ActivityCategoryViewSet(viewsets.ModelViewSet):
    queryset = ActivityCategory.objects.all()
    serializer_class = CoCurricularCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrActivityManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivityCategoryFilter
    search_fields = ['name']


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated, IsAdminOrActivityManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivityFilter
    search_fields = ['name', 'description']


class StudentActivityParticipationViewSet(viewsets.ModelViewSet):
    queryset = StudentActivityParticipation.objects.all()
    serializer_class = StudentActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentActivityParticipationFilter
    search_fields = ['student_profile__student__full_name', 'activity__name']


class EventScheduleViewSet(viewsets.ModelViewSet):
    queryset = ActivityEvent.objects.all()
    serializer_class = ActivityEventSerializer
    permission_classes = [IsAuthenticated, IsCoachOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivityEventFilter
    search_fields = ['name', 'description']


class AwardViewSet(viewsets.ModelViewSet):
    queryset = StudentAward.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentAwardFilter
    search_fields = ['title', 'description', 'level']


class ActivityScheduleViewSet(viewsets.ModelViewSet):
    queryset = ActivitySession.objects.all()
    # serializer_class = ActivityScheduleSerializer
    permission_classes = [IsAuthenticated, IsCoachOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ActivityEventFilter
    search_fields = ['activity__name', 'venue']


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.select_related('student').all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentProfileFilter
    search_fields = ['student__first_name', 'student__last_name', 'current_skill_level']


class CoachFeedbackViewSet(viewsets.ModelViewSet):
    queryset = CoachFeedback.objects.all()
    serializer_class = CoachFeedbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CoachFeedbackFilter
    search_fields = ['activity__name', 'student_profile__student__full_name']


class TalentRecommendationViewSet(viewsets.ModelViewSet):
    queryset = TalentRecommendation.objects.all()
    serializer_class = TalentScoutingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['student__full_name', 'area']


# ============================
# AI + ANALYTICS API VIEWS
# ============================

@api_view(['GET'])
def recommended_activities(request, student_id):
    student = StudentProfile.objects.get(student__id=student_id)
    recommendations = talent_ai.recommend_activities_for_student(student.student)
    return Response({
        'student': student.student.full_name,
        'recommended_activities': [a.name for a in recommendations]
    })


@api_view(['GET'])
def analytics_participation_summary(request):
    return Response(get_participation_summary())


@api_view(['GET'])
def analytics_award_statistics(request):
    return Response(get_award_statistics())


@api_view(['GET'])
def analytics_talent_distribution(request):
    return Response(get_student_talent_distribution())


@api_view(['GET'])
def analytics_activity_popularity(request):
    return Response(get_activity_popularity())


@api_view(['GET'])
def analytics_low_participation_students(request):
    return Response({
        "under_participating_students": [
            s.full_name for s in detect_low_participation_students()
        ]
    })


@api_view(['GET'])
def analytics_gender_disparity(request):
    return Response(detect_gender_disparity_by_activity())


@api_view(['GET'])
def analytics_activity_trends(request):
    return Response(activity_trends_over_time())


@api_view(['GET'])
def analytics_coach_summary(request):
    return Response(coach_performance_summary())
