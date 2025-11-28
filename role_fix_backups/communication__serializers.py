from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    AnnouncementCategory,
    CommunicationAnnouncement,
    CommunicationTarget,
    CommunicationReadLog,
    CommunicationLog,
    AnnouncementAttachment
)
from accounts.serializers import UserSerializer  # Assuming you have this
from institutions.serializers import InstitutionSerializer  # Assuming you have this
User = get_user_model()

class AnnouncementCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementCategory
        fields = ['id', 'description']


class AnnouncementAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementAttachment
        fields = ['id', 'announcement', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class CommunicationTargetSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True, required=False
    )

    class Meta:
        model = CommunicationTarget
        fields = ['id', 'announcement', 'primary_role', 'user', 'user_id', 'class_level', 'stream']


class CommunicationAnnouncementListSerializer(serializers.ModelSerializer):
    category = AnnouncementCategorySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    institution = InstitutionSerializer(read_only=True)
    total_targets = serializers.SerializerMethodField()
    total_reads = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationAnnouncement
        fields = [
            'id', 'title', 'priority', 'author', 'institution', 'category',
            'created_at', 'scheduled_at', 'expires_at',
            'is_public', 'is_approved', 'sent', 'total_targets', 'total_reads']

    def get_total_targets(self, obj):
        return obj.targets.count()

    def get_total_reads(self, obj):
        return obj.read_logs.count()


class CommunicationAnnouncementDetailSerializer(serializers.ModelSerializer):
    category = AnnouncementCategorySerializer(read_only=True)
    author = UserSerializer(read_only=True)
    institution = InstitutionSerializer(read_only=True)
    attachments = AnnouncementAttachmentSerializer(many=True, read_only=True, source='attachments')
    targets = CommunicationTargetSerializer(many=True, read_only=True)
    total_reads = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationAnnouncement
        fields = [
            'id', 'title', 'content', 'priority', 'author', 'institution', 'category',
            'attachments', 'targets', 'scheduled_at', 'created_at', 'updated_at',
            'expires_at', 'is_public', 'is_approved', 'approved_by', 'approved_at',
            'sent', 'channel', 'tags', 'total_reads', 'is_read']

    def get_total_reads(self, obj):
        return obj.read_logs.count()

    def get_is_read(self, obj):
        user = self.context['request'].user
        return obj.read_logs.filter(user=user).exists()


class CommunicationAnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationAnnouncement
        fields = [
            'title', 'content', 'priority', 'institution', 'category',
            'scheduled_at', 'expires_at', 'is_public', 'channel', 'tags'
        ]


class CommunicationReadLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CommunicationReadLog
        fields = ['id', 'announcement', 'user', 'read_at']


class CommunicationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationLog
        fields = ['id', 'announcement', 'timestamp', 'status', 'details']
