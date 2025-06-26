from rest_framework import serializers
from .models import Period, Room, SubjectAssignment, TimetableEntry


class PeriodSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_display', read_only=True)

    class Meta:
        model = Period
        fields = ['id', 'day', 'day_display', 'start_time', 'end_time', 'institution']
        read_only_fields = ['institution']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity', 'is_lab', 'institution']
        read_only_fields = ['institution']


class SubjectAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    stream_name = serializers.CharField(source='stream.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = SubjectAssignment
        fields = [
            'id',
            'teacher', 'teacher_name',
            'subject', 'subject_name',
            'stream', 'stream_name',
            'lessons_per_week',
            'institution', 'institution_name'
        ]
        read_only_fields = ['institution']

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name()


class TimetableEntrySerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    stream_name = serializers.CharField(source='stream.name', read_only=True)
    period_display = serializers.SerializerMethodField()
    room_name = serializers.CharField(source='room.name', read_only=True, default=None)
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = TimetableEntry
        fields = [
            'id',
            'period', 'period_display',
            'stream', 'stream_name',
            'subject', 'subject_name',
            'teacher', 'teacher_name',
            'room', 'room_name',
            'institution', 'institution_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['institution', 'created_at', 'updated_at']

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name()

    def get_period_display(self, obj):
        return f"{obj.period.get_day_display()} {obj.period.start_time.strftime('%H:%M')}–{obj.period.end_time.strftime('%H:%M')}"
