from rest_framework import serializers
from .models import (
    FileCategory, ManagedFile, FileVersion,
    FileAccessLog, SharedAccess,
    AssignmentSubmission, FileAnalytics
)
from accounts.models import CustomUser


class FileCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FileCategory
        fields = '__all__'


class FileVersionSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FileVersion
        fields = '__all__'


class FileAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileAnalytics
        fields = '__all__'


class ManagedFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)
    category = FileCategorySerializer(read_only=True)
    versions = FileVersionSerializer(many=True, read_only=True)
    analytics = FileAnalyticsSerializer(read_only=True)

    class Meta:
        model = ManagedFile
        fields = '__all__'


class ManagedFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagedFile
        fields = [ 'description', 'file', 'file_type',
            'category', 'institution', 'subject', 'class_level', 'stream',
            'student', 'access_scope', 'is_public', 'expires_at', 'tags'
        ]


class FileAccessLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FileAccessLog
        fields = '__all__'


class SharedAccessSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SharedAccess
        fields = '__all__'


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    file = ManagedFileSerializer(read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = '__all__'
