from rest_framework import serializers
from .models import (
    GeneratedReport,
    ReportStudentPerformance,
    ReportSubjectBreakdown
)
from subjects.models import Subject
from students.models import Student
from accounts.models import CustomUser


class ReportStudentPerformanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = ReportStudentPerformance
        fields = [
            'id', 'student', 'student_name',
            'total_marks', 'mean_score', 'grade',
            'rank', 'position_out_of',
            'class_level', 'stream'
        ]


class ReportSubjectBreakdownSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = ReportSubjectBreakdown
        fields = [
            'id', 'subject', 'subject_name', 'teacher', 'teacher_name',
            'class_level', 'stream', 'exam',
            'average_score', 'top_score', 'lowest_score',
            'pass_rate', 'failure_rate', 'most_common_grade'
        ]


class GeneratedReportSerializer(serializers.ModelSerializer):
    student_performances = ReportStudentPerformanceSerializer(many=True, read_only=True)
    subject_breakdowns = ReportSubjectBreakdownSerializer(many=True, read_only=True)

    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'institution', 'report_type', 'access_level',
            'title', 'description', 'generated_by', 'date_generated',
            'is_auto_generated', 'class_level', 'stream',
            'term', 'year', 'file', 'json_data',
            'student_performances', 'subject_breakdowns'
        ]
        read_only_fields = ['id', 'generated_by', 'date_generated', 'json_data']
