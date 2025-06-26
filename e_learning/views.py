from django.shortcuts import render

# Create your views here.
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
    StudentLessonProgress, TeacherActivityLog, AIPredictedScore
)
from .serializers import (
    CourseSerializer, CourseChapterSerializer, LessonSerializer,
    CourseEnrollmentSerializer, CourseCohortLinkSerializer, LiveClassSessionSerializer,
    AssignmentSerializer, AssignmentSubmissionSerializer,
    QuizSerializer, QuizQuestionSerializer, QuizSubmissionSerializer,
    CourseAnnouncementSerializer, MessageSerializer, MessageThreadSerializer,
    StudentLessonProgressSerializer, TeacherActivityLogSerializer, AIPredictedScoreSerializer
)
from institutions.permissions import IsInstitutionMember

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['subject', 'is_published', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Course.objects.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, institution=self.request.user.institution)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['lesson_type']
    search_fields = ['title']
    ordering_fields = ['order']

    def get_queryset(self):
        return Lesson.objects.filter(chapter__course__institution=self.request.user.institution)


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['course']
    search_fields = ['title']
    ordering_fields = ['due_date']

    def get_queryset(self):
        return Assignment.objects.filter(course__institution=self.request.user.institution)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['assignment', 'student']

    def get_queryset(self):
        return AssignmentSubmission.objects.filter(assignment__course__institution=self.request.user.institution)


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return Quiz.objects.filter(course__institution=self.request.user.institution)


class QuizSubmissionViewSet(viewsets.ModelViewSet):
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return QuizSubmission.objects.filter(quiz__course__institution=self.request.user.institution)


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return CourseEnrollment.objects.filter(course__institution=self.request.user.institution)


class LiveClassSessionViewSet(viewsets.ModelViewSet):
    queryset = LiveClassSession.objects.all()
    serializer_class = LiveClassSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return LiveClassSession.objects.filter(course__institution=self.request.user.institution)


class CourseAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = CourseAnnouncement.objects.all()
    serializer_class = CourseAnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return CourseAnnouncement.objects.filter(course__institution=self.request.user.institution)


class StudentLessonProgressViewSet(viewsets.ModelViewSet):
    queryset = StudentLessonProgress.objects.all()
    serializer_class = StudentLessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return StudentLessonProgress.objects.filter(lesson__chapter__course__institution=self.request.user.institution)


class AIPredictedScoreViewSet(viewsets.ModelViewSet):
    queryset = AIPredictedScore.objects.all()
    serializer_class = AIPredictedScoreSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_queryset(self):
        return AIPredictedScore.objects.filter(course__institution=self.request.user.institution)
