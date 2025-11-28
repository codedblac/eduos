from rest_framework import serializers
from .models import (
    ELibraryResource,
    ELibraryTag,
    ELibraryCategory,
    ResourceViewLog,
    ResourceVersion,
    ResourceRating,
    AIAssistedEdit,
)
from subjects.models import Subject
from classes.models import ClassLevel
from accounts.serializers import UserSerializer
from institutions.serializers import InstitutionSerializer


class ELibraryTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ELibraryTag
        fields = ['id']


class ELibraryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ELibraryCategory
        fields = ['id', 'description']


class ResourceVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceVersion
        fields = ['id', 'file', 'uploaded_at', 'notes']


class ResourceRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ResourceRating
        fields = ['id', 'user', 'resource', 'rating', 'review', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class AIAssistedEditSerializer(serializers.ModelSerializer):
    edited_by = UserSerializer(read_only=True)

    class Meta:
        model = AIAssistedEdit
        fields = ['id', 'resource', 'edit_type', 'content_before', 'content_after', 'edited_by', 'edited_at']
        read_only_fields = ['id', 'edited_by', 'edited_at']


class ResourceViewLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ResourceViewLog
        fields = ['id', 'resource', 'user', 'viewed_at', 'action', 'ip_address', 'user_agent']


class ELibraryResourceSerializer(serializers.ModelSerializer):
    uploader = UserSerializer(read_only=True)
    institution = InstitutionSerializer(read_only=True)

    subject = serializers.SlugRelatedField(slug_field="name", read_only=True)
    class_level = serializers.SlugRelatedField(slug_field="name", read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), write_only=True, source="subject")
    class_level_id = serializers.PrimaryKeyRelatedField(queryset=ClassLevel.objects.all(), write_only=True, source="class_level")

    tags = ELibraryTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=ELibraryTag.objects.all(), write_only=True, source="tags")

    category = ELibraryCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=ELibraryCategory.objects.all(), write_only=True, source="category")

    recommended_for = UserSerializer(many=True, read_only=True)
    versions = ResourceVersionSerializer(many=True, read_only=True)
    ratings = ResourceRatingSerializer(many=True, read_only=True)
    ai_edits = AIAssistedEditSerializer(many=True, read_only=True)

    class Meta:
        model = ELibraryResource
        fields = [
            'id', 'institution', 'uploader',
            'title', 'description', 'resource_type',
            'file', 'external_url',
            'subject', 'subject_id', 'class_level', 'class_level_id',
            'tags', 'tag_ids', 'category', 'category_ids',
            'visibility', 'is_approved', 'is_rejected', 'is_deleted',
            'approved_by', 'rejected_by', 'approval_comment', 'approved_at',
            'auto_summary', 'ai_tags',
            'recommended_for', 'view_count', 'download_count',
            'language', 'license_type', 'copyright_holder',
            'created_at', 'updated_at',
            'versions', 'ratings', 'ai_edits']
        read_only_fields = [
            'id', 'institution', 'uploader', 'auto_summary', 'ai_tags',
            'approved_by', 'rejected_by', 'approved_at',
            'view_count', 'download_count', 'created_at', 'updated_at',
            'versions', 'ratings', 'ai_edits', 'recommended_for']


class ELibraryResourceCreateSerializer(serializers.ModelSerializer):
    tag_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=ELibraryTag.objects.all(), write_only=True, source="tags")
    category_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=ELibraryCategory.objects.all(), write_only=True, source="category")
    subject_id = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), write_only=True, source="subject")
    class_level_id = serializers.PrimaryKeyRelatedField(queryset=ClassLevel.objects.all(), write_only=True, source="class_level")

    class Meta:
        model = ELibraryResource
        fields = [
            'title', 'description', 'resource_type', 'file', 'external_url',
            'subject_id', 'class_level_id', 'tag_ids', 'category_ids',
            'visibility', 'language', 'license_type', 'copyright_holder'
        ]
