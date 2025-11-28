from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, Institution, SystemModule


# ---------------------------
# Institution Serializer
# ---------------------------
class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'name', 'is_active', 'created_at']


# ---------------------------
# SystemModule Serializer (Replaces RoleAssignment)
# ---------------------------
class SystemModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemModule
        fields = ["id", "name", "description", "is_default"]


# ---------------------------
# Base User Serializer (General Listing)
# ---------------------------
class UserSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    modules = SystemModuleSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "phone", "primary_role", "modules", "institution",
            "is_active", "is_staff", "date_joined", "last_updated",
            "profile_picture",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# ---------------------------
# User Detail Serializer
# ---------------------------
class UserDetailSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    full_name = serializers.SerializerMethodField()
    modules = SystemModuleSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "phone", "primary_role", "modules",
            "institution", "institution_name",
            "is_active", "is_staff",
            "date_joined", "last_updated",
            "last_login", "last_login_ip", "last_user_agent",
            "profile_picture",
        ]
        read_only_fields = ["id", "email", "institution", "date_joined", "last_login"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# ---------------------------
# User Creation Serializer
# ---------------------------
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    modules = serializers.PrimaryKeyRelatedField(
        queryset=SystemModule.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = [
            "email", "first_name", "last_name", "phone",
            "primary_role", "modules",
            "institution", "password", "profile_picture",
        ]

    def validate(self, data):
        primary_role = data.get("primary_role")
        institution = data.get("institution")

        institutional_roles = [
            CustomUser.Role.INSTITUTION_ADMIN,
            CustomUser.Role.TEACHER,
            CustomUser.Role.STUDENT,
            CustomUser.Role.STAFF,
        ]

        if primary_role in institutional_roles and institution is None:
            raise serializers.ValidationError(
                "Institution is required for institutional roles."
            )

        if primary_role in [
            CustomUser.Role.PUBLIC_LEARNER,
            CustomUser.Role.PUBLIC_TEACHER,
            CustomUser.Role.GOV_USER
        ] and institution is not None:
            raise serializers.ValidationError(
                "Public or government users should not be linked to an institution."
            )

        return data

    def create(self, validated_data):
        modules = validated_data.pop("modules", [])
        password = validated_data.pop("password")

        user = CustomUser.objects.create_user(password=password, **validated_data)

        if modules:
            user.modules.set(modules)

        return user


# ---------------------------
# Public Self-Signup
# ---------------------------
class PublicUserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "phone", "primary_role", "password"]

    def validate(self, data):
        if data.get("primary_role") not in [
            CustomUser.Role.PUBLIC_LEARNER, CustomUser.Role.PUBLIC_TEACHER
        ]:
            raise serializers.ValidationError("Only public user roles allowed here.")
        return data

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


# ---------------------------
# Minimal User Serializer
# ---------------------------
class UserMinimalSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "email", "primary_role", "full_name", "institution"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# ---------------------------
# Change Password
# ---------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


# ---------------------------
# Password Reset
# ---------------------------
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value


# ---------------------------
# JWT Support (email login)
# ---------------------------
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
