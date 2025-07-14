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
router.register(r'curricula', CurriculumViewSet, basename='curriculum')
router.register(r'subject-links', CurriculumSubjectViewSet, basename='curriculum-subject')
router.register(r'topics', SyllabusTopicViewSet, basename='syllabus-topic')
router.register(r'subtopics', SyllabusSubtopicViewSet, basename='syllabus-subtopic')
router.register(r'outcomes', LearningOutcomeViewSet, basename='learning-outcome')
router.register(r'resources', TeachingResourceViewSet, basename='teaching-resource')
router.register(r'progress', SyllabusProgressViewSet, basename='syllabus-progress')
router.register(r'versions', SyllabusVersionViewSet, basename='syllabus-version')
router.register(r'audit-logs', SyllabusAuditLogViewSet, basename='syllabus-audit')

urlpatterns = [
    path('api/', include(router.urls)),
]
