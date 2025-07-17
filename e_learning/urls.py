from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, CourseChapterViewSet, LessonViewSet,
    CourseEnrollmentViewSet, CourseCohortLinkViewSet, LiveClassSessionViewSet,
    AssignmentViewSet, AssignmentSubmissionViewSet,
    QuizViewSet, QuizQuestionViewSet, QuizSubmissionViewSet,
    CourseAnnouncementViewSet, MessageThreadViewSet, MessageViewSet,
    StudentLessonProgressViewSet, TeacherActivityLogViewSet, AIPredictedScoreViewSet,
    CourseCompletionViewSet, CourseReviewViewSet, LessonDiscussionViewSet,
    LessonDownloadLogViewSet, CourseTranslationViewSet, PlagiarismReportViewSet,
    InstructorProfileViewSet, BadgeViewSet, StudentBadgeViewSet, CourseMetadataViewSet
)

router = DefaultRouter()
# Core
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'chapters', CourseChapterViewSet, basename='course-chapter')
router.register(r'lessons', LessonViewSet, basename='lesson')

# Enrollment & Class Mapping
router.register(r'enrollments', CourseEnrollmentViewSet, basename='course-enrollment')
router.register(r'cohorts', CourseCohortLinkViewSet, basename='course-cohort')

# Live Classes
router.register(r'live-classes', LiveClassSessionViewSet, basename='live-class')

# Assignments & Submissions
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'assignment-submissions', AssignmentSubmissionViewSet, basename='assignment-submission')

# Quizzes
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'quiz-questions', QuizQuestionViewSet, basename='quiz-question')
router.register(r'quiz-submissions', QuizSubmissionViewSet, basename='quiz-submission')

# Communication
router.register(r'announcements', CourseAnnouncementViewSet, basename='announcement')
router.register(r'message-threads', MessageThreadViewSet, basename='message-thread')
router.register(r'messages', MessageViewSet, basename='message')

# Analytics
router.register(r'progress', StudentLessonProgressViewSet, basename='lesson-progress')
router.register(r'teacher-logs', TeacherActivityLogViewSet, basename='teacher-log')
router.register(r'ai-scores', AIPredictedScoreViewSet, basename='ai-score')

# Certificates & Reviews
router.register(r'course-completions', CourseCompletionViewSet, basename='course-completion')
router.register(r'course-reviews', CourseReviewViewSet, basename='course-review')

# Discussions & Logs
router.register(r'discussions', LessonDiscussionViewSet, basename='lesson-discussion')
router.register(r'download-logs', LessonDownloadLogViewSet, basename='download-log')
router.register(r'plagiarism-reports', PlagiarismReportViewSet, basename='plagiarism-report')

# Internationalization & Metadata
router.register(r'translations', CourseTranslationViewSet, basename='course-translation')
router.register(r'metadata', CourseMetadataViewSet, basename='course-metadata')

# Instructors & Badges
router.register(r'instructors', InstructorProfileViewSet, basename='instructor')
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'student-badges', StudentBadgeViewSet, basename='student-badge')

urlpatterns = [
    path('', include(router.urls)),
]
