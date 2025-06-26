from rest_framework import serializers
from .models import (
    CoCurricularCategory,
    Activity,
    StudentActivity,
    ActivityEvent,
    ActivityAttendance,
    Award,
    CoachNote,
    TalentScouting
)


class CoCurricularCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CoCurricularCategory
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    category = CoCurricularCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=CoCurricularCategory.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Activity
        fields = '__all__'


class StudentActivitySerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    activity_id = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), source='activity', write_only=True
    )

    class Meta:
        model = StudentActivity
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
    event = ActivityEventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=ActivityEvent.objects.all(), source='event', write_only=True
    )

    class Meta:
        model = ActivityAttendance
        fields = '__all__'


class AwardSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentActivity.objects.values_list('student', flat=True).distinct(), write_only=True, source='student'
    )

    class Meta:
        model = Award
        fields = '__all__'


class CoachNoteSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    activity_id = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), source='activity', write_only=True
    )

    class Meta:
        model = CoachNote
        fields = '__all__'


class TalentScoutingSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentActivity.objects.values_list('student', flat=True).distinct(), write_only=True, source='student'
    )

    class Meta:
        model = TalentScouting
        fields = '__all__'
