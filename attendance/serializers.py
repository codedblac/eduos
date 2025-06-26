from rest_framework import serializers
from .models import (
    SchoolAttendanceRecord,
    ClassAttendanceRecord,
    AbsenceReason
)
from students.models import Student
from classes.models import Subject, ClassLevel, Stream
from timetable.models import TimetableEntry
from accounts.models import CustomUser as User


class AbsenceReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceReason
        fields = ['id', 'institution', 'reason', 'default']
        read_only_fields = ['id', 'institution']


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
