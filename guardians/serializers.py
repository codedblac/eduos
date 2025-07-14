from rest_framework import serializers
from .models import Guardian, GuardianStudentLink, GuardianNotification
from students.models import Student
from accounts.serializers import UserMiniSerializer  # Mini user serializer (already assumed)

# ✅ Guardian Serializer (Read-Only View)
class GuardianSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = Guardian
        fields = [
            'id',
            'user',
            'institution',
            'phone_number',
            'email',
            'id_number',
            'occupation',
            'address',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ✅ Guardian Creation / Update Serializer (Write-Only)
class GuardianCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = [
            'user',
            'institution',
            'phone_number',
            'email',
            'id_number',
            'occupation',
            'address',
            'is_active',
        ]


# ✅ GuardianStudentLink Full Serializer (Readable View)
class GuardianStudentLinkSerializer(serializers.ModelSerializer):
    guardian = GuardianSerializer(read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = GuardianStudentLink
        fields = [
            'id',
            'guardian',
            'student',
            'relationship',
            'is_primary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ✅ GuardianStudentLink Create/Update Serializer
class GuardianStudentLinkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianStudentLink
        fields = [
            'guardian',
            'student',
            'relationship',
            'is_primary',
        ]


# ✅ Guardian Notification Serializer (Fully Readable)
class GuardianNotificationSerializer(serializers.ModelSerializer):
    guardian = GuardianSerializer(read_only=True)

    class Meta:
        model = GuardianNotification
        fields = [
            'id',
            'guardian',
            'institution',
            'title',
            'message',
            'type',
            'related_object_type',
            'related_object_id',
            'is_read',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp', 'guardian']
