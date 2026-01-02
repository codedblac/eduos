# institutions/serializers.py

from rest_framework import serializers
from .models import (
    Institution, 
    SchoolAccount, 
    SchoolRegistrationRequest, 
    InstitutionType, 
    SchoolType
)
from modules.models import SystemModule
from accounts.models import CustomUser


# ================================================================
# ✅ 1. Minimal Serializer
# ================================================================
class InstitutionMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'code', 'name', 'status']


# ================================================================
# 🏫 2. Institution Serializers
# ================================================================
class InstitutionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True
    )
    class Meta:
        model = Institution
        fields = [
            'id', 'code', 'registration_number',
            'name', 'status', 'status_display', 'country', 'county', 'sub_county', 'ward', 'village',
            'address', 'phone', 'email', 'website',
            'logo', 'primary_color', 'secondary_color', 'theme_mode',
            'school_type', 'institution_type', 'ownership', 'funding_source',
            'established_year', 'created_at', 'updated_at', 'extra_info'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

# ================================================================
# 🔒 Institution Status Control (Admin/System Only)
# ================================================================
class InstitutionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['status']


class InstitutionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            'name', 'code', 'registration_number',
            'country', 'county', 'sub_county', 'ward', 'village',
            'address', 'phone', 'email', 'website',
            'logo', 'primary_color', 'secondary_color', 'theme_mode',
            'school_type', 'institution_type', 'ownership', 'funding_source',
            'established_year', 'extra_info'
        ]

    def validate_code(self, value):
        qs = Institution.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Institution code must be unique.")
        return value


# ================================================================
# 💳 3. School Account Serializers
# ================================================================
class SchoolAccountSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = SchoolAccount
        fields = [
            'id', 'institution', 'institution_name',
            'account_name', 'account_number', 'bank_name',
            'branch', 'payment_type', 'mpesa_till_number',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SchoolAccountCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolAccount
        fields = [
            'institution', 'account_name', 'account_number',
            'bank_name', 'branch', 'payment_type',
            'mpesa_till_number', 'is_default'
        ]

    def validate(self, data):
        payment_type = data.get('payment_type')

        if payment_type == SchoolAccount.BANK:
            if not data.get('bank_name') or not data.get('account_number'):
                raise serializers.ValidationError("Bank name and account number required for bank accounts.")
        elif payment_type == SchoolAccount.MOBILE_MONEY:
            if not data.get('mpesa_till_number'):
                raise serializers.ValidationError("Mpesa till number required for mobile money accounts.")
        else:
            raise serializers.ValidationError("Invalid payment type.")

        return data

    def create(self, validated_data):
        if validated_data.get('is_default'):
            SchoolAccount.objects.filter(
                institution=validated_data['institution'],
                is_default=True
            ).update(is_default=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('is_default') and not instance.is_default:
            SchoolAccount.objects.filter(
                institution=instance.institution,
                is_default=True
            ).update(is_default=False)
        return super().update(instance, validated_data)


# ================================================================
# 📝 4. School Registration Request Serializers
# ================================================================
class SchoolRegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolRegistrationRequest
        fields = [
            'id', 'school_name', 'code', 'country', 'county',
            'sub_county', 'ward', 'village',
            'email', 'phone', 'institution_type', 'school_type',
            'submitted_at', 'approved', 'approved_at', 'admin_created'
        ]
        read_only_fields = [
            'id', 'submitted_at', 'approved', 'approved_at', 'admin_created'
        ]


class SchoolRegistrationRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolRegistrationRequest
        fields = [
            'school_name', 'code', 'country', 'county',
            'sub_county', 'ward', 'village',
            'email', 'phone', 'institution_type', 'school_type'
        ]

    def validate_code(self, value):
        if SchoolRegistrationRequest.objects.filter(code=value).exists():
            raise serializers.ValidationError("A registration request with this code already exists.")
        if Institution.objects.filter(code=value).exists():
            raise serializers.ValidationError("An institution with this code already exists.")
        return value


# ================================================================
# 🚀 5. Institution Onboarding Serializer
# ================================================================
class InstitutionOnboardingSerializer(serializers.Serializer):
    """
    Serializer for DRF onboarding endpoint.
    Supports plan selection, optional module IDs, and admin creation.
    """

    # Institution info
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=50)
    country = serializers.CharField(max_length=100)
    county = serializers.CharField(max_length=100)
    sub_county = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ward = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    village = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField()
    website = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    primary_color = serializers.CharField(required=False, default="#0047AB")
    secondary_color = serializers.CharField(required=False, default="#FFFFFF")
    theme_mode = serializers.ChoiceField(
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )

    school_type = serializers.ChoiceField(choices=SchoolType.choices)
    institution_type = serializers.ChoiceField(choices=InstitutionType.choices)
    ownership = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    funding_source = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    established_year = serializers.IntegerField(required=False, allow_null=True)

    # Admin info
    password = serializers.CharField(write_only=True, min_length=8)

    # Modules and plan
    module_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    default_package = serializers.ChoiceField(
        choices=[('BASIC', 'Basic'), ('PRO', 'Pro'), ('ENTERPRISE', 'Enterprise'), ('CUSTOM', 'Custom')],
        required=False,
        allow_null=True
    )

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_module_ids(self, value):
        if not value:
            return value
        existing_count = SystemModule.objects.filter(id__in=value).count()
        if existing_count != len(value):
            raise serializers.ValidationError("Some provided modules do not exist.")
        return value
