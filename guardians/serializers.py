from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import (
    Guardian,
    GuardianStudentLink,
    GuardianNotification
)
from accounts.serializers import UserSerializer
from students.serializers import StudentSerializer
from institutions.serializers import InstitutionSerializer
from students.models import Student


class GuardianSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    institution = InstitutionSerializer(read_only=True)
    student_ids = serializers.SerializerMethodField()

    class Meta:
        model = Guardian
        fields = [
            'id', 'user', 'institution', 'phone_number', 'email', 'id_number',
            'occupation', 'address', 'profile_photo', 'preferred_language',
            'notification_preferences', 'is_active', 'is_deleted',
            'created_at', 'updated_at', 'student_ids'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_student_ids(self, obj):
        return [link.student.id for link in obj.student_links.all()]


class GuardianCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = [
            'user', 'institution', 'phone_number', 'email', 'id_number',
            'occupation', 'address', 'profile_photo', 'preferred_language',
            'notification_preferences'
        ]


class GuardianStudentLinkSerializer(serializers.ModelSerializer):
    guardian = GuardianSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), write_only=True, source='student')

    class Meta:
        model = GuardianStudentLink
        fields = [
            'id', 'guardian', 'student', 'student_id', 'relationship', 'is_primary',
            'verified_by_school', 'notes', 'start_date', 'end_date', 'is_deleted',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GuardianNotificationSerializer(serializers.ModelSerializer):
    guardian = GuardianSerializer(read_only=True)
    institution = InstitutionSerializer(read_only=True)
    content_type = serializers.SlugRelatedField(
        slug_field='model', queryset=ContentType.objects.all(), required=False
    )
    object_id = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = GuardianNotification
        fields = [
            'id', 'guardian', 'institution', 'title', 'message', 'type',
            'priority', 'delivered_via', 'content_type', 'object_id',
            'is_read', 'read_at', 'scheduled_for', 'timestamp', 'is_deleted'
        ]
        read_only_fields = ['id', 'timestamp', 'read_at']
