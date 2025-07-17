from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import (
    Course, CourseChapter, Lesson,
    CourseEnrollment, CourseCohortLink, LiveClassSession,
    Assignment, AssignmentSubmission,
    Quiz, QuizQuestion, QuizSubmission,
    CourseAnnouncement, Message, MessageThread,
    StudentLessonProgress, TeacherActivityLog, AIPredictedScore,
    CourseCompletion, CourseReview, LessonDiscussion,
    LessonDownloadLog, CourseTranslation, PlagiarismReport,
    InstructorProfile, Badge, StudentBadge, CourseMetadata
)

from .serializers import (
    CourseSerializer, CourseChapterSerializer, LessonSerializer,
    CourseEnrollmentSerializer, CourseCohortLinkSerializer, LiveClassSessionSerializer,
    AssignmentSerializer, AssignmentSubmissionSerializer,
    QuizSerializer, QuizQuestionSerializer, QuizSubmissionSerializer,
    CourseAnnouncementSerializer, MessageSerializer, MessageThreadSerializer,
    StudentLessonProgressSerializer, TeacherActivityLogSerializer, AIPredictedScoreSerializer,
    CourseCompletionSerializer, CourseReviewSerializer, LessonDiscussionSerializer,
    LessonDownloadLogSerializer, CourseTranslationSerializer, PlagiarismReportSerializer,
    InstructorProfileSerializer, BadgeSerializer, StudentBadgeSerializer, CourseMetadataSerializer
)

from institutions.permissions import IsInstitutionMember

# Generic ViewSet Boilerplate
class BaseInstitutionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return self.queryset.filter(**self._institution_filter())

    def perform_create(self, serializer):
        serializer.save(**self._creation_kwargs())

    def _institution_filter(self):
        return {'course__institution': self.request.user.institution} if 'course__institution' in str(self.queryset.query) else {'institution': self.request.user.institution}

    def _creation_kwargs(self):
        return {'institution': self.request.user.institution, 'created_by': self.request.user} if 'institution' in self.serializer_class.Meta.fields else {'created_by': self.request.user}


class CourseViewSet(BaseInstitutionViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['subject', 'is_published', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']


class CourseChapterViewSet(BaseInstitutionViewSet):
    queryset = CourseChapter.objects.all()
    serializer_class = CourseChapterSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['order']


class LessonViewSet(BaseInstitutionViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['lesson_type']
    search_fields = ['title']
    ordering_fields = ['order']


class AssignmentViewSet(BaseInstitutionViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['course']
    search_fields = ['title']
    ordering_fields = ['due_date']


class AssignmentSubmissionViewSet(BaseInstitutionViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['assignment', 'student']


class QuizViewSet(BaseInstitutionViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]


class QuizQuestionViewSet(BaseInstitutionViewSet):
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer
    filter_backends = [DjangoFilterBackend]


class QuizSubmissionViewSet(BaseInstitutionViewSet):
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer
    filter_backends = [DjangoFilterBackend]


class CourseEnrollmentViewSet(BaseInstitutionViewSet):
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    filter_backends = [DjangoFilterBackend]


class CourseCohortLinkViewSet(BaseInstitutionViewSet):
    queryset = CourseCohortLink.objects.all()
    serializer_class = CourseCohortLinkSerializer


class LiveClassSessionViewSet(BaseInstitutionViewSet):
    queryset = LiveClassSession.objects.all()
    serializer_class = LiveClassSessionSerializer


class CourseAnnouncementViewSet(BaseInstitutionViewSet):
    queryset = CourseAnnouncement.objects.all()
    serializer_class = CourseAnnouncementSerializer


class MessageThreadViewSet(BaseInstitutionViewSet):
    queryset = MessageThread.objects.all()
    serializer_class = MessageThreadSerializer


class MessageViewSet(BaseInstitutionViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class StudentLessonProgressViewSet(BaseInstitutionViewSet):
    queryset = StudentLessonProgress.objects.all()
    serializer_class = StudentLessonProgressSerializer


class TeacherActivityLogViewSet(BaseInstitutionViewSet):
    queryset = TeacherActivityLog.objects.all()
    serializer_class = TeacherActivityLogSerializer


class AIPredictedScoreViewSet(BaseInstitutionViewSet):
    queryset = AIPredictedScore.objects.all()
    serializer_class = AIPredictedScoreSerializer


class CourseCompletionViewSet(BaseInstitutionViewSet):
    queryset = CourseCompletion.objects.all()
    serializer_class = CourseCompletionSerializer


class CourseReviewViewSet(BaseInstitutionViewSet):
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer


class LessonDiscussionViewSet(BaseInstitutionViewSet):
    queryset = LessonDiscussion.objects.all()
    serializer_class = LessonDiscussionSerializer


class LessonDownloadLogViewSet(BaseInstitutionViewSet):
    queryset = LessonDownloadLog.objects.all()
    serializer_class = LessonDownloadLogSerializer


class CourseTranslationViewSet(BaseInstitutionViewSet):
    queryset = CourseTranslation.objects.all()
    serializer_class = CourseTranslationSerializer


class PlagiarismReportViewSet(BaseInstitutionViewSet):
    queryset = PlagiarismReport.objects.all()
    serializer_class = PlagiarismReportSerializer


class InstructorProfileViewSet(BaseInstitutionViewSet):
    queryset = InstructorProfile.objects.all()
    serializer_class = InstructorProfileSerializer


class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentBadgeViewSet(BaseInstitutionViewSet):
    queryset = StudentBadge.objects.all()
    serializer_class = StudentBadgeSerializer


class CourseMetadataViewSet(BaseInstitutionViewSet):
    queryset = CourseMetadata.objects.all()
    serializer_class = CourseMetadataSerializer
