from rest_framework import serializers
from .models import (
    Event,
    EventRSVP,
    EventAttendance,
    EventFeedback,
    EventAttachment,
    EventTag,
    RecurringEventRule,
    EventComment,
)
from accounts.serializers import UserMinimalSerializer
from students.serializers import StudentSerializer
from accounts.models import CustomUser
from students.models import Student
from classes.models import ClassLevel, Stream


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
    tags = EventTagSerializer(many=True, read_only=True)
    recurring_rule = RecurringEventRuleSerializer(read_only=True)

    # Write-only fields for creation
    tag_ids = serializers.PrimaryKeyRelatedField(queryset=EventTag.objects.all(), many=True, write_only=True, required=False)
    attachment_ids = serializers.PrimaryKeyRelatedField(queryset=EventAttachment.objects.all(), many=True, write_only=True, required=False)
    recurring_rule_id = serializers.PrimaryKeyRelatedField(queryset=RecurringEventRule.objects.all(), write_only=True, allow_null=True, required=False)

    class Meta:
        model = Event
        fields = [
            'id', 'institution', 'title', 'description', 'event_type', 'location',
            'is_virtual', 'virtual_link', 'media_attachments', 'tags', 'start_time', 'end_time',
            'is_all_day', 'is_recurring', 'recurring_rule', 'recurring_rule_id',
            'target_roles', 'target_users', 'target_students', 'target_class_levels', 'target_streams',
            'requires_rsvp', 'allow_feedback', 'allow_comments', 'max_attendees',
            'created_by', 'created_at', 'updated_at', 'is_active',
            'tag_ids', 'attachment_ids',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'media_attachments', 'tags']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['created_by'] = request.user
        validated_data['institution'] = request.user.institution

        tags = validated_data.pop('tag_ids', [])
        attachments = validated_data.pop('attachment_ids', [])
        recurring_rule = validated_data.pop('recurring_rule_id', None)

        event = super().create(validated_data)

        if tags:
            event.tags.set(tags)
        if attachments:
            event.media_attachments.set(attachments)
        if recurring_rule:
            event.recurring_rule = recurring_rule
            event.save()

        return event

    def validate(self, data):
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
    recorded_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = EventAttendance
        fields = ['id', 'event', 'user', 'is_present', 'timestamp', 'recorded_by']
        read_only_fields = ['user', 'timestamp', 'recorded_by']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['recorded_by'] = self.context['request'].user
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


class EventCommentSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = EventComment
        fields = ['id', 'event', 'user', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
