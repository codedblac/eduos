from rest_framework import serializers
from .models import (
    AbsenceReason,
    SchoolAttendanceRecord,
    ClassAttendanceRecord,
    AttendancePolicy,
    DailyAttendanceSummary,
    AttendanceDeviceLog
)
from students.models import Student
from classes.models import ClassLevel, Stream
from subjects.models import Subject
from timetable.models import TimetableEntry
from accounts.models import CustomUser as User


class AbsenceReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceReason
        fields = ['id', 'institution', 'reason', 'default']
        read_only_fields = ['id', 'institution']

    def create(self, validated_data):
        validated_data['institution'] = self.context['request'].user.institution
        return super().create(validated_data)


class SchoolAttendanceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = SchoolAttendanceRecord
        fields = [
            'id', 'institution', 'user', 'date',
            'entry_time', 'exit_time', 'source',
            'recorded_by', 'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_by', 'recorded_at', 'institution']

    def create(self, validated_data):
        validated_data['institution'] = self.context['request'].user.institution
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class ClassAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), required=False)
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), required=False)
    timetable_entry = serializers.PrimaryKeyRelatedField(queryset=TimetableEntry.objects.all(), required=False)
    class_level = serializers.PrimaryKeyRelatedField(queryset=ClassLevel.objects.all(), required=False)
    stream = serializers.PrimaryKeyRelatedField(queryset=Stream.objects.all(), required=False)
    reason = serializers.PrimaryKeyRelatedField(queryset=AbsenceReason.objects.all(), required=False, allow_null=True)

    class Meta:
        model = ClassAttendanceRecord
        fields = [
            'id', 'institution', 'date', 'source',
            'student', 'teacher', 'class_level', 'stream',
            'subject', 'timetable_entry', 'status',
            'reason', 'custom_reason',
            'recorded_by', 'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_by', 'recorded_at', 'institution']

    def create(self, validated_data):
        validated_data['institution'] = self.context['request'].user.institution
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


class AttendancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendancePolicy
        fields = [
            'id', 'institution', 'user_type', 'min_entry_time',
            'max_entry_time', 'min_exit_time', 'max_exit_time',
            'require_exit', 'enforce_timetable'
        ]
        read_only_fields = ['id', 'institution']

    def create(self, validated_data):
        validated_data['institution'] = self.context['request'].user.institution
        return super().create(validated_data)


class DailyAttendanceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAttendanceSummary
        fields = [
            'id', 'institution', 'user_type', 'date',
            'total_expected', 'present', 'absent', 'late',
            'summary_generated_at'
        ]
        read_only_fields = ['id', 'summary_generated_at']


class AttendanceDeviceLogSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = AttendanceDeviceLog
        fields = [
            'id', 'institution', 'user', 'timestamp',
            'device_id', 'entry_or_exit', 'status',
            'raw_data', 'log_source'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['institution'] = self.context['request'].user.institution
        return super().create(validated_data)
