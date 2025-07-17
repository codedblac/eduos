from rest_framework import serializers
from .models import (
    ActivityCategory,
    Activity,
    StudentActivityParticipation,
    ActivityEvent,
    ActivityAttendance,
    StudentAward,
    StudentReflection,
    TalentRecommendation,
    StudentProfile,
    CoachFeedback,
    ActivityPerformance,
    CoachAssignmentHistory
)
from students.models import Student
from django.contrib.auth import get_user_model

User = get_user_model()


class CoCurricularCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCategory
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    category = CoCurricularCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ActivityCategory.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Activity
        fields = '__all__'


class CoachAssignmentHistorySerializer(serializers.ModelSerializer):
    coach = serializers.StringRelatedField(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='coach', write_only=True)

    class Meta:
        model = CoachAssignmentHistory
        fields = '__all__'


class StudentProfileSerializer(serializers.ModelSerializer):
    preferred_categories = CoCurricularCategorySerializer(many=True, read_only=True)
    preferred_categories_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ActivityCategory.objects.all(), source='preferred_categories', write_only=True
    )

    class Meta:
        model = StudentProfile
        fields = '__all__'


class StudentActivitySerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    activity_id = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), source='activity', write_only=True
    )
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )

    class Meta:
        model = StudentActivityParticipation
        fields = '__all__'


class CoachFeedbackSerializer(serializers.ModelSerializer):
    coach = serializers.StringRelatedField(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='coach', write_only=True
    )
    participation = StudentActivitySerializer(read_only=True)
    participation_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentActivityParticipation.objects.all(), source='participation', write_only=True
    )

    class Meta:
        model = CoachFeedback
        fields = '__all__'


class ActivityPerformanceSerializer(serializers.ModelSerializer):
    participation = StudentActivitySerializer(read_only=True)
    participation_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentActivityParticipation.objects.all(), source='participation', write_only=True
    )

    class Meta:
        model = ActivityPerformance
        fields = '__all__'


class ActivityEventSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    activity_id = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), source='activity', write_only=True
    )

    class Meta:
        model = ActivityEvent
        fields = '__all__'


class ActivityAttendanceSerializer(serializers.ModelSerializer):
    session = serializers.StringRelatedField(read_only=True)
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=ActivityEvent.objects.all(), source='session', write_only=True
    )
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )

    class Meta:
        model = ActivityAttendance
        fields = '__all__'


class AwardSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )
    activity = ActivitySerializer(read_only=True)
    activity_id = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), source='activity', write_only=True
    )

    class Meta:
        model = StudentAward
        fields = '__all__'


class CoachNoteSerializer(serializers.ModelSerializer):
    participation = StudentActivitySerializer(read_only=True)
    participation_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentActivityParticipation.objects.all(), source='participation', write_only=True
    )
    author = serializers.StringRelatedField(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='author', write_only=True
    )

    class Meta:
        model = StudentReflection
        fields = '__all__'


class TalentScoutingSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )
    suggested_by = serializers.StringRelatedField(read_only=True)
    suggested_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='suggested_by', write_only=True
    )

    class Meta:
        model = TalentRecommendation
        fields = '__all__'
