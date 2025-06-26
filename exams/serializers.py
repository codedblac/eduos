# exams/serializers.py

from rest_framework import serializers
from .models import (
    Exam, ExamSubject, StudentScore,
    GradeBoundary, ExamInsight, ExamPrediction
)
from subjects.models import Subject
from students.models import Student
from teachers.models import Teacher

from classes.models import Stream, ClassLevel


# -----------------------------
# Basic Subject Serializer
# -----------------------------
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


# -----------------------------
# Student Serializer (Simplified)
# -----------------------------
class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'full_name', 'admission_number']


# -----------------------------
# Teacher Serializer (Simplified)
# -----------------------------
class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'full_name']


# -----------------------------
# Exam Serializers
# -----------------------------

class ExamSerializer(serializers.ModelSerializer):
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)

    class Meta:
        model = Exam
        fields = '__all__'


class ExamSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)

    class Meta:
        model = ExamSubject
        fields = ['id', 'exam', 'subject', 'subject_name', 'teacher', 'teacher_name', 'max_score']


class StudentScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    admission_number = serializers.CharField(source='student.admission_number', read_only=True)

    class Meta:
        model = StudentScore
        fields = ['id', 'exam_subject', 'student', 'student_name', 'admission_number', 'score', 'grade', 'remarks', 'position']
        read_only_fields = ['grade', 'position', 'remarks']


# -----------------------------
# Grade Boundary Serializer
# -----------------------------

class GradeBoundarySerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = GradeBoundary
        fields = ['id', 'institution', 'subject', 'subject_name', 'grade', 'min_score', 'max_score']


# -----------------------------
# Exam Insights Serializer
# -----------------------------

class ExamInsightSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = ExamInsight
        fields = [
            'id', 'exam', 'subject', 'subject_name',
            'average_score', 'highest_score', 'lowest_score',
            'most_common_grade', 'insight_summary', 'generated_at'
        ]


# -----------------------------
# AI Prediction Serializer
# -----------------------------

class ExamPredictionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)

    class Meta:
        model = ExamPrediction
        fields = [
            'id', 'subject', 'subject_name',
            'class_level', 'class_level_name',
            'stream', 'stream_name',
            'term', 'year', 'institution',
            'predicted_questions', 'auto_generated_exam', 'auto_generated_marking_scheme',
            'source_summary', 'created_by', 'created_at'
        ]
