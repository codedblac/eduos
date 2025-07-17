from rest_framework import serializers
from .models import (
    AssessmentType, AssessmentTemplate, Assessment, Question, AnswerChoice,
    AssessmentSession, StudentAnswer, MarkingScheme, GradingRubric,
    Feedback, RetakePolicy, AssessmentGroup, AssessmentWeight,
    AssessmentLock, AssessmentVisibility, PerformanceTrend, CodeTestCase
)
from accounts.serializers import UserSerializer  
from subjects.serializers import SubjectSerializer, ClassLevelSerializer  

# === Core Serializers ===

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


class AssessmentWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentWeight
        fields = '__all__'


# === Assessment & Nested Serializers ===

class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = '__all__'


class CodeTestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeTestCase
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    answer_choices = AnswerChoiceSerializer(many=True, read_only=True)
    code_test_cases = CodeTestCaseSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'


class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    class_level = ClassLevelSerializer(read_only=True)
    group = AssessmentGroupSerializer(read_only=True)

    class Meta:
        model = Assessment
        fields = '__all__'


# === Sessions & Answers ===

class AssessmentSessionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    assessment = AssessmentSerializer(read_only=True)

    class Meta:
        model = AssessmentSession
        fields = '__all__'


class StudentAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    student = UserSerializer(read_only=True)
    session = AssessmentSessionSerializer(read_only=True)

    class Meta:
        model = StudentAnswer
        fields = '__all__'


# === Marking, Grading & Feedback ===

class MarkingSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkingScheme
        fields = '__all__'


class GradingRubricSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingRubric
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    assessment = AssessmentSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'


# === Policies & Settings ===

class RetakePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RetakePolicy
        fields = '__all__'


class AssessmentLockSerializer(serializers.ModelSerializer):
    locked_by = UserSerializer(read_only=True)

    class Meta:
        model = AssessmentLock
        fields = '__all__'


class AssessmentVisibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentVisibility
        fields = '__all__'


# === Analytics ===

class PerformanceTrendSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = PerformanceTrend
        fields = '__all__'
