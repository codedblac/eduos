from rest_framework import serializers
from .models import (
    Curriculum, CurriculumSubject, SyllabusTopic, SyllabusSubtopic,
    LearningOutcome, TeachingResource, SyllabusProgress, SyllabusVersion, SyllabusAuditLog
)
from subjects.models import Subject, ClassLevel, Term
from institutions.models import Institution
from django.contrib.auth import get_user_model

User = get_user_model()


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']

    def get_full_name(self, obj):
        return obj.get_full_name()


class CurriculumSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(read_only=True)

    class Meta:
        model = Curriculum
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'code']


class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ['id', 'code']


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['id', 'order']


class CurriculumSubjectSerializer(serializers.ModelSerializer):
    curriculum = CurriculumSerializer(read_only=True)
    curriculum_id = serializers.PrimaryKeyRelatedField(
        queryset=Curriculum.objects.all(), source='curriculum', write_only=True
    )
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), source='subject', write_only=True
    )
    class_level = ClassLevelSerializer(read_only=True)
    class_level_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(), source='class_level', write_only=True
    )
    term = TermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=Term.objects.all(), source='term', write_only=True
    )

    class Meta:
        model = CurriculumSubject
        fields = [
            'id', 'curriculum', 'curriculum_id', 'subject', 'subject_id',
            'class_level', 'class_level_id', 'term', 'term_id', 'ordering'
        ]


class SyllabusSubtopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyllabusSubtopic
        fields = ['id', 'title', 'notes', 'order', 'topic']


class LearningOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningOutcome
        fields = ['id', 'description', 'competency_area', 'indicators', 'order', 'topic']


class TeachingResourceSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.get_full_name')

    class Meta:
        model = TeachingResource
        fields = [
            'id', 'title', 'type', 'file', 'url', 'subtopic', 'outcome',
            'uploaded_by', 'uploaded_by_name', 'created_at'
        ]


class SyllabusTopicSerializer(serializers.ModelSerializer):
    subtopics = SyllabusSubtopicSerializer(many=True, read_only=True)
    outcomes = LearningOutcomeSerializer(many=True, read_only=True)
    curriculum_subject_display = serializers.StringRelatedField(source='curriculum_subject', read_only=True)
    curriculum_subject_id = serializers.PrimaryKeyRelatedField(
        queryset=CurriculumSubject.objects.all(),
        source='curriculum_subject',
        write_only=True
    )

    class Meta:
        model = SyllabusTopic
        fields = [
            'id', 'title', 'description', 'bloom_taxonomy_level', 'difficulty',
            'estimated_duration_minutes', 'order', 'curriculum_subject_id',
            'curriculum_subject_display', 'subtopics', 'outcomes'
        ]


class SyllabusProgressSerializer(serializers.ModelSerializer):
    topic_title = serializers.ReadOnlyField(source='topic.title')
    teacher_name = serializers.ReadOnlyField(source='teacher.get_full_name')

    class Meta:
        model = SyllabusProgress
        fields = ['id', 'topic', 'topic_title', 'teacher', 'teacher_name', 'status', 'coverage_date', 'notes']


class SyllabusVersionSerializer(serializers.ModelSerializer):
    curriculum_subject_display = serializers.StringRelatedField(source='curriculum_subject', read_only=True)
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')

    class Meta:
        model = SyllabusVersion
        fields = ['id', 'curriculum_subject', 'curriculum_subject_display', 'version_number', 'change_log', 'created_by', 'created_by_name', 'created_at']


class SyllabusAuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    curriculum_subject_display = serializers.StringRelatedField(source='curriculum_subject', read_only=True)
    topic_title = serializers.StringRelatedField(source='topic', read_only=True)

    class Meta:
        model = SyllabusAuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'timestamp',
            'curriculum_subject', 'curriculum_subject_display',
            'topic', 'topic_title', 'notes'
        ]
