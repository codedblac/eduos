import django_filters
from django.db.models import Q
from .models import (
    Course, CourseChapter, Lesson, Assignment, AssignmentSubmission,
    Quiz, QuizSubmission, LiveClassSession, CourseEnrollment, CourseCohortLink,
    CourseAnnouncement, Message, MessageThread,
    StudentLessonProgress, TeacherActivityLog, AIPredictedScore,
    CourseCompletion, CourseReview, LessonDiscussion,
    LessonDownloadLog, CourseTranslation, PlagiarismReport,
    InstructorProfile, Badge, StudentBadge, CourseMetadata
)

class CourseFilter(django_filters.FilterSet):
    subject = django_filters.NumberFilter(field_name='subject_id')
    institution = django_filters.NumberFilter(field_name='institution_id')
    is_published = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    created_by = django_filters.NumberFilter(field_name='created_by_id')

    class Meta:
        model = Course
        fields = ['subject', 'institution', 'is_published', 'is_featured', 'created_by']


class LessonFilter(django_filters.FilterSet):
    chapter = django_filters.NumberFilter(field_name='chapter_id')
    lesson_type = django_filters.CharFilter(lookup_expr='iexact')
    order = django_filters.NumberFilter()

    class Meta:
        model = Lesson
        fields = ['chapter', 'lesson_type', 'order']


class AssignmentFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')
    due_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Assignment
        fields = ['course', 'due_date']


class AssignmentSubmissionFilter(django_filters.FilterSet):
    assignment = django_filters.NumberFilter(field_name='assignment_id')
    student = django_filters.NumberFilter(field_name='student_id')
    submitted_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = AssignmentSubmission
        fields = ['assignment', 'student', 'submitted_at']


class QuizFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')
    is_timed = django_filters.BooleanFilter()
    start_time = django_filters.DateFromToRangeFilter()
    end_time = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Quiz
        fields = ['course', 'is_timed', 'start_time', 'end_time']


class QuizSubmissionFilter(django_filters.FilterSet):
    quiz = django_filters.NumberFilter(field_name='quiz_id')
    student = django_filters.NumberFilter(field_name='student_id')
    submitted_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = QuizSubmission
        fields = ['quiz', 'student', 'submitted_at']


class LiveClassSessionFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')
    start_time = django_filters.DateFromToRangeFilter()
    platform = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = LiveClassSession
        fields = ['course', 'platform', 'start_time']


class CourseEnrollmentFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    course = django_filters.NumberFilter(field_name='course_id')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = CourseEnrollment
        fields = ['student', 'course', 'is_active']


class CourseCohortLinkFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')
    class_level = django_filters.NumberFilter(field_name='class_level_id')
    stream = django_filters.NumberFilter(field_name='stream_id')

    class Meta:
        model = CourseCohortLink
        fields = ['course', 'class_level', 'stream']


class CourseAnnouncementFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')
    created_by = django_filters.NumberFilter(field_name='created_by_id')

    class Meta:
        model = CourseAnnouncement
        fields = ['course', 'created_by']


class MessageThreadFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')
    participant = django_filters.NumberFilter(method='filter_by_participant')

    def filter_by_participant(self, queryset, name, value):
        return queryset.filter(participants__id=value)

    class Meta:
        model = MessageThread
        fields = ['course']


class MessageFilter(django_filters.FilterSet):
    thread = django_filters.NumberFilter(field_name='thread_id')
    sender = django_filters.NumberFilter(field_name='sender_id')
    timestamp = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Message
        fields = ['thread', 'sender', 'timestamp']


class StudentLessonProgressFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    lesson = django_filters.NumberFilter(field_name='lesson_id')
    is_completed = django_filters.BooleanFilter()

    class Meta:
        model = StudentLessonProgress
        fields = ['student', 'lesson', 'is_completed']


class AIPredictedScoreFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    course = django_filters.NumberFilter(field_name='course_id')

    class Meta:
        model = AIPredictedScore
        fields = ['student', 'course']


class CourseReviewFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')
    student = django_filters.NumberFilter(field_name='student_id')
    rating = django_filters.RangeFilter()

    class Meta:
        model = CourseReview
        fields = ['course', 'student', 'rating']


class CourseCompletionFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')
    student = django_filters.NumberFilter(field_name='student_id')
    certificate_issued = django_filters.BooleanFilter()

    class Meta:
        model = CourseCompletion
        fields = ['course', 'student', 'certificate_issued']


class PlagiarismReportFilter(django_filters.FilterSet):
    submission = django_filters.NumberFilter(field_name='submission_id')
    similarity_score = django_filters.RangeFilter()

    class Meta:
        model = PlagiarismReport
        fields = ['submission', 'similarity_score']


class LessonDownloadLogFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    lesson = django_filters.NumberFilter(field_name='lesson_id')
    downloaded_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = LessonDownloadLog
        fields = ['student', 'lesson', 'downloaded_at']


class CourseTranslationFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')
    language_code = django_filters.CharFilter()

    class Meta:
        model = CourseTranslation
        fields = ['course', 'language_code']


class InstructorProfileFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name='user_id')
    expertise = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = InstructorProfile
        fields = ['user', 'expertise']


class StudentBadgeFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    badge = django_filters.NumberFilter(field_name='badge_id')

    class Meta:
        model = StudentBadge
        fields = ['student', 'badge']


class CourseMetadataFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name='course_id')

    class Meta:
        model = CourseMetadata
        fields = ['course']
