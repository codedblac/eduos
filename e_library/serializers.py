from rest_framework import serializers
from .models import (
    ELibraryResource,
    ELibraryTag,
    ResourceViewLog,
    ResourceVersion,
)
from subjects.models import Subject
from classes.models import ClassLevel
from accounts.serializers import UserMiniSerializer  # Assume this gives user id, name, role

class ELibraryTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ELibraryTag
        fields = ['id', 'name']


class ResourceVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceVersion
        fields = ['id', 'file', 'uploaded_at', 'notes']


class ELibraryResourceSerializer(serializers.ModelSerializer):
    uploader = UserMiniSerializer(read_only=True)
    tags = ELibraryTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ELibraryTag.objects.all(), write_only=True, source="tags"
    )
    subject = serializers.SlugRelatedField(slug_field="name", read_only=True)
    class_level = serializers.SlugRelatedField(slug_field="name", read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), write_only=True, source="subject")
    class_level_id = serializers.PrimaryKeyRelatedField(queryset=ClassLevel.objects.all(), write_only=True, source="class_level")

    versions = ResourceVersionSerializer(many=True, read_only=True)
    recommended_for = UserMiniSerializer(many=True, read_only=True)

    class Meta:
        model = ELibraryResource
        fields = [
            'id', 'institution', 'uploader',
            'title', 'description', 'resource_type',
            'file', 'external_url',
            'subject', 'subject_id', 'class_level', 'class_level_id',
            'tags', 'tag_ids',
            'visibility', 'is_approved',
            'auto_summary', 'recommended_for',
            'created_at', 'updated_at',
            'versions',
        ]
        read_only_fields = ['id', 'institution', 'uploader', 'auto_summary', 'recommended_for']


class ELibraryResourceCreateSerializer(serializers.ModelSerializer):
    """
    Use this for upload endpoints. Auto-assigns uploader and institution from view.
    """
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ELibraryTag.objects.all(), write_only=True, source="tags"
    )
    subject_id = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), write_only=True, source="subject")
    class_level_id = serializers.PrimaryKeyRelatedField(queryset=ClassLevel.objects.all(), write_only=True, source="class_level")

    class Meta:
        model = ELibraryResource
        fields = [
            'title', 'description', 'resource_type', 'file', 'external_url',
            'subject_id', 'class_level_id', 'tag_ids', 'visibility'
        ]


class ResourceViewLogSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = ResourceViewLog
        fields = ['id', 'resource', 'user', 'viewed_at']
