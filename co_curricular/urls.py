from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityCategoryViewSet,
    ActivityViewSet,
    StudentActivityParticipationViewSet,
    CoCurricularEventViewSet,
    TalentProfileViewSet,
    AwardViewSet,
    ActivityScheduleViewSet,
    recommended_activities,
    talent_analytics_overview,
    participation_trends,
    underrepresented_groups,
)

# DRF router for ViewSets
router = DefaultRouter()
router.register(r'activity-categories', ActivityCategoryViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'participations', StudentActivityParticipationViewSet)
router.register(r'events', CoCurricularEventViewSet)
router.register(r'talent-profiles', TalentProfileViewSet)
router.register(r'awards', AwardViewSet)
router.register(r'schedules', ActivityScheduleViewSet)

urlpatterns = [
    # Auto-routed ViewSets
    path('', include(router.urls)),

    # AI Endpoints
    path('ai/recommend/<int:student_id>/', recommended_activities, name='ai-recommend-activities'),

    # Analytics Endpoints
    path('analytics/overview/', talent_analytics_overview, name='talent-analytics-overview'),
    path('analytics/participation-trends/', participation_trends, name='participation-trends'),
    path('analytics/underrepresented-groups/', underrepresented_groups, name='underrepresented-groups'),
]
