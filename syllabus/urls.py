from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    CurriculumViewSet,
    CurriculumSubjectViewSet,
    SyllabusTopicViewSet,
    SyllabusSubtopicViewSet,
    LearningOutcomeViewSet,
    TeachingResourceViewSet,
    SyllabusProgressViewSet,
    SyllabusVersionViewSet,
    SyllabusAuditLogViewSet,
)

router = DefaultRouter()
router.register(r'curricula', CurriculumViewSet)
router.register(r'subject-links', CurriculumSubjectViewSet)
router.register(r'topics', SyllabusTopicViewSet)
router.register(r'subtopics', SyllabusSubtopicViewSet)
router.register(r'outcomes', LearningOutcomeViewSet)
router.register(r'resources', TeachingResourceViewSet)
router.register(r'progress', SyllabusProgressViewSet)
router.register(r'versions', SyllabusVersionViewSet)
router.register(r'audit-logs', SyllabusAuditLogViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
