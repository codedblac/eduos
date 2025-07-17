from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityCategoryViewSet,
    ActivityViewSet,
    StudentActivityParticipationViewSet,
    EventScheduleViewSet,
    StudentProfileViewSet,
    AwardViewSet,
    ActivityScheduleViewSet,
    CoachFeedbackViewSet,
    TalentRecommendationViewSet,

    # AI and Analytics endpoints
    recommended_activities,
    analytics_participation_summary,
    analytics_award_statistics,
    analytics_talent_distribution,
    analytics_activity_popularity,
    analytics_low_participation_students,
    analytics_gender_disparity,
    analytics_activity_trends,
    analytics_coach_summary
)

# DRF router for ViewSets
router = DefaultRouter()
router.register(r'activity-categories', ActivityCategoryViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'participations', StudentActivityParticipationViewSet)
router.register(r'events', EventScheduleViewSet)
router.register(r'talent-profiles', StudentProfileViewSet)
router.register(r'awards', AwardViewSet)
router.register(r'schedules', ActivityScheduleViewSet)
router.register(r'coach-feedback', CoachFeedbackViewSet)
router.register(r'recommendations', TalentRecommendationViewSet)

urlpatterns = [
    # Auto-routed ViewSets
    path('', include(router.urls)),

    # AI Endpoint
    path('ai/recommend/<int:student_id>/', recommended_activities, name='ai-recommend-activities'),

    # Analytics Endpoints
    path('analytics/participation-summary/', analytics_participation_summary, name='analytics-participation-summary'),
    path('analytics/award-statistics/', analytics_award_statistics, name='analytics-award-statistics'),
    path('analytics/talent-distribution/', analytics_talent_distribution, name='analytics-talent-distribution'),
    path('analytics/activity-popularity/', analytics_activity_popularity, name='analytics-activity-popularity'),
    path('analytics/low-participation/', analytics_low_participation_students, name='analytics-low-participation'),
    path('analytics/gender-disparity/', analytics_gender_disparity, name='analytics-gender-disparity'),
    path('analytics/activity-trends/', analytics_activity_trends, name='analytics-activity-trends'),
    path('analytics/coach-summary/', analytics_coach_summary, name='analytics-coach-summary'),
]
