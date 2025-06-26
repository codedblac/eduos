from rest_framework import serializers
from .models import LessonPlan, LessonSchedule, LessonSession, LessonAttachment
from subjects.models import Subject, ClassLevel
from syllabus.models import SyllabusTopic, SyllabusSubtopic
from academics.models import Term
from institutions.models import Institution
from accounts.models import CustomUser


class LessonAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonAttachment
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'uploaded_at']


class LessonSessionSerializer(serializers.ModelSerializer):
    attachments = LessonAttachmentSerializer(many=True, read_only=True)
    recorded_by_name = serializers.StringRelatedField(source='recorded_by', read_only=True)

    class Meta:
        model = LessonSession
        fields = '__all__'
        read_only_fields = ['created_at', 'recorded_by']


class LessonScheduleSerializer(serializers.ModelSerializer):
    session = LessonSessionSerializer(read_only=True)

    class Meta:
        model = LessonSchedule
        fields = '__all__'


class LessonPlanSerializer(serializers.ModelSerializer):
    schedules = LessonScheduleSerializer(many=True, read_only=True)
    institution_name = serializers.StringRelatedField(source='institution', read_only=True)
    subject_name = serializers.StringRelatedField(source='subject', read_only=True)
    class_level_name = serializers.StringRelatedField(source='class_level', read_only=True)
    teacher_name = serializers.StringRelatedField(source='teacher', read_only=True)
    topic_title = serializers.StringRelatedField(source='topic', read_only=True)
    subtopic_title = serializers.StringRelatedField(source='subtopic', read_only=True)

    class Meta:
        model = LessonPlan
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
