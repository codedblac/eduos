from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Institution



#  Institution Serializer


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'name', 'is_active', 'created_at']



#  Base User Serializer


class UserSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'institution', 'is_active', 'is_staff',
            'date_joined', 'last_updated', 'profile_picture',
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"



#  User Detail Serializer


class UserDetailSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'institution', 'institution_name',
            'is_active', 'is_staff', 'date_joined', 'last_updated',
            'last_login', 'last_login_ip', 'last_user_agent', 'profile_picture',
        ]
        read_only_fields = ['id', 'email', 'role', 'institution', 'date_joined', 'last_login']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"



#  User Creation Serializer


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'role', 'institution', 'password', 'profile_picture'
        ]

    def validate(self, data):
        role = data.get("role")
        institution = data.get("institution")

        if role in [
            CustomUser.Role.ADMIN, CustomUser.Role.TEACHER,
            CustomUser.Role.STUDENT, CustomUser.Role.LIBRARIAN,
            CustomUser.Role.BURSAR, CustomUser.Role.STORE_KEEPER,
            CustomUser.Role.HOSTEL_MANAGER, CustomUser.Role.FINANCE,
            CustomUser.Role.SUPPORT_STAFF
        ] and institution is None:
            raise serializers.ValidationError("Institution is required for institutional roles.")

        if role in [
            CustomUser.Role.PUBLIC_LEARNER,
            CustomUser.Role.PUBLIC_TEACHER,
            CustomUser.Role.GOV_USER
        ] and institution is not None:
            raise serializers.ValidationError("Public or government users should not be linked to an institution.")

        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        return CustomUser.objects.create_user(password=password, **validated_data)



#  Public Self-Signup Serializer


class PublicUserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'role', 'password']

    def validate(self, data):
        if data.get("role") not in [CustomUser.Role.PUBLIC_LEARNER, CustomUser.Role.PUBLIC_TEACHER]:
            raise serializers.ValidationError("Only public learner or teacher roles allowed for this route.")
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        return CustomUser.objects.create_user(password=password, **validated_data)



#  Minimal Serializer for Account Switching


class UserMinimalSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'role', 'full_name', 'institution']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"



#  Change Password Serializer


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value



#  Password Reset Flow Serializers


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value
