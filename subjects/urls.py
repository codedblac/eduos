from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SubjectViewSet,
    SubjectClassLevelViewSet,
    SubjectTeacherViewSet,
    SubjectCategoryViewSet,
    SubjectPrerequisiteViewSet,
    SubjectAssessmentWeightViewSet,
    SubjectGradingSchemeViewSet,
    SubjectResourceViewSet,
    SubjectVersionViewSet,
    SubjectAIView,
    SubjectAnalyticsView
)

from rest_framework.routers import DefaultRouter
from .views import SubjectAssignmentViewSet

router = DefaultRouter()
router.register(r'subject-assignments', SubjectAssignmentViewSet, basename='subject-assignment')

urlpatterns = router.urls

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subjects')
router.register(r'subject-class-levels', SubjectClassLevelViewSet, basename='subject-class-levels')
router.register(r'subject-teachers', SubjectTeacherViewSet, basename='subject-teachers')
router.register(r'subject-categories', SubjectCategoryViewSet, basename='subject-categories')
router.register(r'subject-prerequisites', SubjectPrerequisiteViewSet, basename='subject-prerequisites')
router.register(r'subject-assessment-weights', SubjectAssessmentWeightViewSet, basename='subject-assessment-weights')
router.register(r'subject-grading-schemes', SubjectGradingSchemeViewSet, basename='subject-grading-schemes')
router.register(r'subject-resources', SubjectResourceViewSet, basename='subject-resources')
router.register(r'subject-versions', SubjectVersionViewSet, basename='subject-versions')

urlpatterns = [
    path('api/v1/', include(router.urls)),

    # AI + Analytics
    path('api/v1/insights/ai/', SubjectAIView.as_view(), name='subject-ai-insights'),
    path('api/v1/insights/analytics/', SubjectAnalyticsView.as_view(), name='subject-analytics-insights'),
]
