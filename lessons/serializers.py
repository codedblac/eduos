from rest_framework import serializers
from .models import (
    LessonPlan, LessonSchedule, LessonSession,
    LessonAttachment, LessonFeedback, LessonTemplate,LessonScaffoldSuggestion
)


class LessonAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonAttachment
        fields = '__all__'


class LessonFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonFeedback
        fields = '__all__'


class LessonSessionSerializer(serializers.ModelSerializer):
    attachments = LessonAttachmentSerializer(many=True, read_only=True)
    feedbacks = LessonFeedbackSerializer(many=True, read_only=True)

    class Meta:
        model = LessonSession
        fields = '__all__'


class LessonScheduleSerializer(serializers.ModelSerializer):
    session = LessonSessionSerializer(read_only=True)

    class Meta:
        model = LessonSchedule
        fields = '__all__'


class LessonPlanSerializer(serializers.ModelSerializer):
    schedules = LessonScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = LessonPlan
        fields = '__all__'


class LessonTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonTemplate
        fields = '__all__'
from rest_framework import serializers
from .models import LessonScaffoldSuggestion

class LessonScaffoldSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonScaffoldSuggestion
        fields = '__all__'
