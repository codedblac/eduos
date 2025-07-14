# institutions/serializers.py

from rest_framework import serializers
from .models import Institution, SchoolAccount, InstitutionType, SchoolType

# ==========================
# ✅ MINIMAL SERIALIZERS
# ==========================

class InstitutionMinimalSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer used in nested representations and dropdowns.
    """
    class Meta:
        model = Institution
        fields = ['id', 'name', 'code']


# ==========================
# 🏫 Institution Serializers
# ==========================

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            'id', 'name', 'code', 'registration_number',
            'country', 'county', 'sub_county', 'ward', 'village',
            'address', 'phone', 'email', 'website',
            'logo', 'primary_color', 'secondary_color', 'theme_mode',
            'school_type', 'institution_type', 'ownership', 'funding_source',
            'established_year', 'created_at', 'updated_at', 'extra_info',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstitutionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            'name', 'code', 'registration_number',
            'country', 'county', 'sub_county', 'ward', 'village',
            'address', 'phone', 'email', 'website',
            'logo', 'primary_color', 'secondary_color', 'theme_mode',
            'school_type', 'institution_type', 'ownership', 'funding_source',
            'established_year', 'extra_info',
        ]

    def validate_code(self, value):
        qs = Institution.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Institution code must be unique.")
        return value


# ==========================
# 💰 School Account Serializers
# ==========================

class SchoolAccountSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = SchoolAccount
        fields = [
            'id', 'institution', 'institution_name',
            'account_name', 'account_number', 'bank_name',
            'branch', 'payment_type', 'mpesa_till_number',
            'is_default', 'created_at', 'updated_at',
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
            if not data.get('bank_name'):
                raise serializers.ValidationError("Bank name is required for bank accounts.")
            if not data.get('account_number'):
                raise serializers.ValidationError("Account number is required for bank accounts.")
        elif payment_type == SchoolAccount.MOBILE_MONEY:
            if not data.get('mpesa_till_number'):
                raise serializers.ValidationError("Mpesa till number is required for mobile money accounts.")
        else:
            raise serializers.ValidationError("Invalid payment type.")

        return data

    def create(self, validated_data):
        if validated_data.get('is_default'):
            SchoolAccount.objects.filter(
                institution=validated_data['institution'], is_default=True
            ).update(is_default=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('is_default') and not instance.is_default:
            SchoolAccount.objects.filter(
                institution=instance.institution, is_default=True
            ).update(is_default=False)
        return super().update(instance, validated_data)
