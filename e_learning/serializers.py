from rest_framework import serializers
from .models import (
    Course, CourseChapter, Lesson,
    CourseEnrollment, CourseCohortLink, LiveClassSession,
    Assignment, AssignmentSubmission,
    Quiz, QuizQuestion, QuizSubmission,
    CourseAnnouncement, Message, MessageThread,
    StudentLessonProgress, TeacherActivityLog, AIPredictedScore
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
