from rest_framework import serializers
from .models import (
    AssessmentType, AssessmentTemplate, Assessment, Question, AnswerChoice,
    AssessmentSession, StudentAnswer, MarkingScheme, GradingRubric,
    Feedback, RetakePolicy, AssessmentGroup, AssessmentWeight,
    AssessmentLock, AssessmentVisibility, PerformanceTrend, CodeTestCase
)


class AssessmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentType
        fields = '__all__'


class AssessmentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentTemplate
        fields = '__all__'


class AssessmentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentGroup
        fields = '__all__'


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = '__all__'


class CodeTestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTestCase
        fields = '__all__'


class AssessmentSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentSession
        fields = '__all__'


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = '__all__'


class MarkingSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkingScheme
        fields = '__all__'


class GradingRubricSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingRubric
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class RetakePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RetakePolicy
        fields = '__all__'


class AssessmentWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentWeight
        fields = '__all__'


class AssessmentLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentLock
        fields = '__all__'


class AssessmentVisibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentVisibility
        fields = '__all__'


class PerformanceTrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceTrend
        fields = '__all__'
