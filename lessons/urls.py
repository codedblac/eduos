from rest_framework.routers import DefaultRouter
from django.urls import path, include
from lessons.views import (
    LessonPlanViewSet, LessonSessionViewSet,
    LessonScheduleViewSet, LessonAttachmentViewSet,
    LessonAnalyticsViewSet
)

router = DefaultRouter()
router.register(r'lesson-plans', LessonPlanViewSet)
router.register(r'lesson-sessions', LessonSessionViewSet)
router.register(r'lesson-schedules', LessonScheduleViewSet)
router.register(r'lesson-attachments', LessonAttachmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', LessonAnalyticsViewSet.as_view({'get': 'list'}), name='lesson-analytics'),
]
