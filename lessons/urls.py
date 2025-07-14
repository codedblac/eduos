from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LessonPlanViewSet, LessonScheduleViewSet, LessonSessionViewSet,
    LessonAttachmentViewSet, LessonScaffoldSuggestionViewSet,
    LessonAISuggestionAPIView, LessonCoverageAlertAPIView,
    LessonAnalyticsSummaryAPIView, TeacherLessonAnalyticsAPIView,
    InstitutionLessonAnalyticsAPIView
)

router = DefaultRouter()
router.register(r'plans', LessonPlanViewSet)
router.register(r'schedules', LessonScheduleViewSet)
router.register(r'sessions', LessonSessionViewSet)
router.register(r'attachments', LessonAttachmentViewSet)
router.register(r'scaffold-suggestions', LessonScaffoldSuggestionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),

    # AI Views
    path('api/ai/plan/<int:lesson_plan_id>/suggestions/', LessonAISuggestionAPIView.as_view()),
    path('api/ai/coverage-alerts/', LessonCoverageAlertAPIView.as_view()),

    # Analytics Views
    path('api/analytics/summary/', LessonAnalyticsSummaryAPIView.as_view()),
    path('api/analytics/teacher/<int:teacher_id>/', TeacherLessonAnalyticsAPIView.as_view()),
    path('api/analytics/institution/<int:institution_id>/', InstitutionLessonAnalyticsAPIView.as_view()),
]
