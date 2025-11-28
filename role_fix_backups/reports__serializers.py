# reports/serializers.py

from rest_framework import serializers
from .models import (
    GeneratedReport, ReportStudentPerformance, ReportSubjectBreakdown,
    ReportAuditTrail, ReportPrintRequest
)
from institutions.models import Institution
from students.models import Student
from classes.models import ClassLevel, Stream
from subjects.models import Subject
from exams.models import Exam
from accounts.models import CustomUser


# ---------------------------------------------
# Nested / Related Field Serializers
# ---------------------------------------------

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'admission_number', 'user']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'code']


class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ['id']


class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ['id']


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'term', 'year']


# ---------------------------------------------
# Core Report Serializers
# ---------------------------------------------

class ReportStudentPerformanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    class_level = ClassLevelSerializer(read_only=True)
    stream = StreamSerializer(read_only=True)

    class Meta:
        model = ReportStudentPerformance
        fields = [
            'id', 'student', 'total_marks', 'mean_score', 'grade', 'rank',
            'position_out_of', 'class_level', 'stream', 'comment',
            'remedial_suggestion', 'flagged', 'created_at'
        ]


class ReportSubjectBreakdownSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    teacher = CustomUserSerializer(read_only=True)
    class_level = ClassLevelSerializer(read_only=True)
    stream = StreamSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = ReportSubjectBreakdown
        fields = [
            'id', 'subject', 'teacher', 'class_level', 'stream', 'exam',
            'average_score', 'top_score', 'lowest_score', 'pass_rate',
            'failure_rate', 'most_common_grade', 'comment', 'flagged'
        ]


class GeneratedReportSerializer(serializers.ModelSerializer):
    generated_by = CustomUserSerializer(read_only=True)
    institution = serializers.StringRelatedField()
    class_level = ClassLevelSerializer(read_only=True)
    stream = StreamSerializer(read_only=True)

    student_performances = ReportStudentPerformanceSerializer(many=True, read_only=True)
    subject_breakdowns = ReportSubjectBreakdownSerializer(many=True, read_only=True)

    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'title', 'description', 'report_type', 'access_level', 'status',
            'generated_by', 'institution', 'class_level', 'stream', 'term', 'year',
            'date_generated', 'updated_at', 'is_auto_generated', 'is_active',
            'version', 'file', 'json_data', 'ai_summary', 'smart_flags',
            'student_performances', 'subject_breakdowns'
        ]


# ---------------------------------------------
# Utility Serializers
# ---------------------------------------------

class ReportAuditTrailSerializer(serializers.ModelSerializer):
    performed_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = ReportAuditTrail
        fields = ['id', 'report', 'action', 'performed_by', 'timestamp']


class ReportPrintRequestSerializer(serializers.ModelSerializer):
    requested_by = CustomUserSerializer(read_only=True)
    report = serializers.StringRelatedField()

    class Meta:
        model = ReportPrintRequest
        fields = [
            'id', 'report', 'requested_by', 'requested_at', 'copies',
            'print_center_notes', 'printed_file', 'is_printed', 'printed_at'
        ]
