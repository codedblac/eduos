from rest_framework import serializers
from .models import (
    Curriculum, CurriculumSubject, SyllabusTopic, SyllabusSubtopic,
    LearningOutcome, TeachingResource, SyllabusProgress, SyllabusVersion, SyllabusAuditLog
)
from subjects.models import Subject, ClassLevel, Term


class CurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ['id', 'name']


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['id', 'name']


class CurriculumSubjectSerializer(serializers.ModelSerializer):
    curriculum = CurriculumSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    class_level = ClassLevelSerializer(read_only=True)
    term = TermSerializer(read_only=True)

    class Meta:
        model = CurriculumSubject
        fields = '__all__'


class SyllabusSubtopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyllabusSubtopic
        fields = '__all__'


class LearningOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningOutcome
        fields = '__all__'


class TeachingResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeachingResource
        fields = '__all__'


class SyllabusTopicSerializer(serializers.ModelSerializer):
    subtopics = SyllabusSubtopicSerializer(many=True, read_only=True)
    outcomes = LearningOutcomeSerializer(many=True, read_only=True)

    class Meta:
        model = SyllabusTopic
        fields = '__all__'


class SyllabusProgressSerializer(serializers.ModelSerializer):
    topic_title = serializers.ReadOnlyField(source='topic.title')
    teacher_name = serializers.ReadOnlyField(source='teacher.get_full_name')

    class Meta:
        model = SyllabusProgress
        fields = '__all__'


class SyllabusVersionSerializer(serializers.ModelSerializer):
    curriculum_subject_display = serializers.StringRelatedField(source='curriculum_subject', read_only=True)
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')

    class Meta:
        model = SyllabusVersion
        fields = '__all__'


class SyllabusAuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    curriculum_subject_display = serializers.StringRelatedField(source='curriculum_subject', read_only=True)
    topic_title = serializers.StringRelatedField(source='topic', read_only=True)

    class Meta:
        model = SyllabusAuditLog
        fields = '__all__'
