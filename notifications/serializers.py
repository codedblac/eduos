from rest_framework import serializers
from .models import (
    Notification,
    NotificationDelivery,
    NotificationPreference,
)
from students.models import Student
from classes.models import ClassLevel, Stream
from accounts.serializers import UserMinimalSerializer  

class NotificationSerializer(serializers.ModelSerializer):
    target_users = UserMinimalSerializer(many=True, read_only=True)
    target_users_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Notification._meta.get_field('target_users').remote_field.model.objects.all(), write_only=True, required=False
    )
    target_students = serializers.PrimaryKeyRelatedField(many=True, queryset=Student.objects.all(), required=False)
    target_class_levels = serializers.PrimaryKeyRelatedField(many=True, queryset=ClassLevel.objects.all(), required=False)
    target_streams = serializers.PrimaryKeyRelatedField(many=True, queryset=Stream.objects.all(), required=False)

    class Meta:
        model = Notification
        fields = [
            'id', 'institution', 'title', 'message', 'notification_type', 'channels',
            'created_by', 'created_at', 'target_roles', 'target_users', 'target_users_ids',
            'target_students', 'target_class_levels', 'target_streams', 'is_active'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'target_users']

    def create(self, validated_data):
        target_users_ids = validated_data.pop('target_users_ids', [])
        notification = Notification.objects.create(**validated_data)
        notification.target_users.set(target_users_ids)
        return notification

    def update(self, instance, validated_data):
        target_users_ids = validated_data.pop('target_users_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if target_users_ids is not None:
            instance.target_users.set(target_users_ids)
        return instance


class NotificationDeliverySerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = NotificationDelivery
        fields = ['id', 'notification', 'user', 'channel', 'delivered', 'read', 'delivered_at', 'read_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['id', 'user', 'allow_email', 'allow_sms', 'allow_push', 'allow_in_app']
        read_only_fields = ['user']
