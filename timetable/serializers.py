from rest_framework import serializers
from .models import (
    PeriodTemplate, Room, SubjectAssignment,
    TimetableVersion, TimetableEntry,
    TimetableNotificationSetting, TimetableChangeLog,
    TeacherAvailabilityOverride
)


class PeriodTemplateSerializer(serializers.ModelSerializer):
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = PeriodTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class RoomSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = Room
        fields = '__all__'


class SubjectAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = SubjectAssignment
        fields = '__all__'


class TimetableVersionSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = TimetableVersion
        fields = '__all__'


class TimetableEntrySerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    version_term = serializers.CharField(source='version.term.name', read_only=True)
    day = serializers.CharField(source='period_template.day', read_only=True)
    start_time = serializers.TimeField(source='period_template.start_time', read_only=True)
    end_time = serializers.TimeField(source='period_template.end_time', read_only=True)

    class Meta:
        model = TimetableEntry
        fields = '__all__'


class TimetableNotificationSettingSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = TimetableNotificationSetting
        fields = '__all__'


class TimetableChangeLogSerializer(serializers.ModelSerializer):
    entry_display = serializers.StringRelatedField(source='entry', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    subject = serializers.CharField(source='entry.subject.name', read_only=True)
    stream = serializers.CharField(source='entry.stream.name', read_only=True)
    period_day = serializers.CharField(source='entry.period_template.day', read_only=True)
    timestamp_formatted = serializers.DateTimeField(source='timestamp', format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = TimetableChangeLog
        fields = '__all__'


class TeacherAvailabilityOverrideSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)

    class Meta:
        model = TeacherAvailabilityOverride
        fields = '__all__'
