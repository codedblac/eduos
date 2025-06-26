from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, LessonViewSet, AssignmentViewSet,
    AssignmentSubmissionViewSet, QuizViewSet, QuizSubmissionViewSet,
    CourseEnrollmentViewSet, LiveClassSessionViewSet,
    CourseAnnouncementViewSet, StudentLessonProgressViewSet,
    AIPredictedScoreViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'assignment-submissions', AssignmentSubmissionViewSet, basename='assignment-submission')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'quiz-submissions', QuizSubmissionViewSet, basename='quiz-submission')
router.register(r'enrollments', CourseEnrollmentViewSet, basename='course-enrollment')
router.register(r'live-classes', LiveClassSessionViewSet, basename='live-class')
router.register(r'announcements', CourseAnnouncementViewSet, basename='course-announcement')
router.register(r'progress', StudentLessonProgressViewSet, basename='lesson-progress')
router.register(r'ai-scores', AIPredictedScoreViewSet, basename='ai-score')

urlpatterns = [
    path('', include(router.urls)),
]
