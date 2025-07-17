from rest_framework import serializers
from .models import (
    Course, CourseChapter, Lesson,
    CourseEnrollment, CourseCohortLink, LiveClassSession,
    Assignment, AssignmentSubmission,
    Quiz, QuizQuestion, QuizSubmission,
    CourseAnnouncement, Message, MessageThread,
    StudentLessonProgress, TeacherActivityLog, AIPredictedScore,
    InstructorProfile, CourseTag, CourseCertificate, CourseReview, LessonDiscussion
)
from .models import (
    Badge, StudentBadge, CourseMetadata,
    LessonDownloadLog, CourseTranslation, PlagiarismReport,
    CourseCompletion
)

# ------------------------------
# Nested Lesson Serializer
# ------------------------------

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseChapterSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = CourseChapter
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    chapters = CourseChapterSerializer(many=True, read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Course
        fields = '__all__'


# ------------------------------
# Enrollment & Class Mapping
# ------------------------------

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = '__all__'


class CourseCohortLinkSerializer(serializers.ModelSerializer):
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)

    class Meta:
        model = CourseCohortLink
        fields = '__all__'


# ------------------------------
# Live Classes
# ------------------------------

class LiveClassSessionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = LiveClassSession
        fields = '__all__'


# ------------------------------
# Assignments
# ------------------------------

class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = '__all__'


# ------------------------------
# Quizzes
# ------------------------------

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = '__all__'


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'


class QuizSubmissionSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = QuizSubmission
        fields = '__all__'


# ------------------------------
# Messaging & Announcements
# ------------------------------

class CourseAnnouncementSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = CourseAnnouncement
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class MessageThreadSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = MessageThread
        fields = '__all__'


# ------------------------------
# Analytics
# ------------------------------

class StudentLessonProgressSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = StudentLessonProgress
        fields = '__all__'


class TeacherActivityLogSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = TeacherActivityLog
        fields = '__all__'


# ------------------------------
# AI Predictions
# ------------------------------

class AIPredictedScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = AIPredictedScore
        fields = '__all__'


# ------------------------------
# Extras
# ------------------------------

class InstructorProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = InstructorProfile
        fields = '__all__'


class CourseTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTag
        fields = '__all__'


class CourseCertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = CourseCertificate
        fields = '__all__'


class CourseReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = CourseReview
        fields = '__all__'


class LessonDiscussionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = LessonDiscussion
        fields = '__all__'

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'

class StudentBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentBadge
        fields = '__all__'

class CourseMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMetadata
        fields = '__all__'

class LessonDownloadLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonDownloadLog
        fields = '__all__'

class CourseTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTranslation
        fields = '__all__'

class PlagiarismReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlagiarismReport
        fields = '__all__'

class CourseCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCompletion
        fields = '__all__'