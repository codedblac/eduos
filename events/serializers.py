from rest_framework import serializers
from .models import (
    Event,
    EventRSVP,
    EventAttendance,
    EventFeedback,
    EventAttachment,
    EventTag,
    RecurringEventRule
)
from accounts.serializers import UserMinimalSerializer  # optional
from students.serializers import StudentMinimalSerializer  # optional


class EventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTag
        fields = ['id', 'name', 'color']


class EventAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = EventAttachment
        fields = ['id', 'file', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']


class RecurringEventRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringEventRule
        fields = ['id', 'frequency', 'interval', 'end_date', 'exceptions']


class EventSerializer(serializers.ModelSerializer):
    created_by = UserMinimalSerializer(read_only=True)
    media_attachments = EventAttachmentSerializer(many=True, read_only=True)
    tags = EventTagSerializer(many=True, required=False)
    recurring_rule = RecurringEventRuleSerializer(required=False, allow_null=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'institution',
            'title',
            'description',
            'event_type',
            'location',
            'is_virtual',
            'virtual_link',
            'media_attachments',
            'tags',
            'start_time',
            'end_time',
            'is_all_day',
            'is_recurring',
            'recurring_rule',
            'target_roles',
            'target_users',
            'target_students',
            'target_class_levels',
            'target_streams',
            'requires_rsvp',
            'allow_feedback',
            'created_by',
            'created_at',
            'is_active',
        ]
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        """
        Add institutional scoping and future conflict detection logic hook here.
        """
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("Start time must be before end time.")
        return data


class EventRSVPSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = EventRSVP
        fields = ['id', 'event', 'user', 'response', 'responded_at']
        read_only_fields = ['user', 'responded_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class EventAttendanceSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = EventAttendance
        fields = ['id', 'event', 'user', 'is_present', 'timestamp']
        read_only_fields = ['user', 'timestamp']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class EventFeedbackSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = EventFeedback
        fields = ['id', 'event', 'user', 'rating', 'comment', 'submitted_at']
        read_only_fields = ['user', 'submitted_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
