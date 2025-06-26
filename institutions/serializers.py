# institutions/serializers.py
from rest_framework import serializers
from .models import Institution, SchoolAccount

class SchoolAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolAccount
        fields = [
            'id', 'account_name', 'account_number', 'bank_name',
            'branch', 'payment_type', 'mpesa_till_number', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class InstitutionSerializer(serializers.ModelSerializer):
    accounts = SchoolAccountSerializer(many=True, read_only=True)

    class Meta:
        model = Institution
        fields = [
            'id', 'name', 'code', 'registration_number',
            'country', 'county', 'sub_county', 'ward', 'village',
            'phone_number', 'email', 'website',
            'logo', 'theme_color',
            'school_type', 'ownership', 'funding_source',
            'established_year', 'extra_info',
            'accounts',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
