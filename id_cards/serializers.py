from rest_framework import serializers
from .models import (
    IDCardTemplate,
    IDCard,
    IDCardAuditLog,
    IDCardReissueRequest,
    DigitalIDToken,
)
from institutions.serializers import InstitutionSerializer
from accounts.serializers import UserSerializer
from django.contrib.contenttypes.models import ContentType


class IDCardTemplateSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(
        queryset=IDCardTemplate._meta.get_field('institution').related_model.objects.all(),
        source='institution',
        write_only=True
    )

    class Meta:
        model = IDCardTemplate
        fields = [
            'id', 'name', 'institution', 'institution_id',
            'background_color', 'text_color', 'font', 'include_qr_code',
            'include_barcode', 'include_signature', 'logo',
            'background_image', 'active', 'created_at'
        ]
        read_only_fields = ['created_at']


class IDCardSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(
        queryset=IDCard._meta.get_field('institution').related_model.objects.all(),
        source='institution',
        write_only=True
    )
    template_id = serializers.PrimaryKeyRelatedField(
        queryset=IDCard._meta.get_field('template').related_model.objects.all(),
        source='template',
        write_only=True
    )
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=IDCard._meta.get_field('user').related_model.objects.all(),
        source='user',
        write_only=True,
        required=False,
        allow_null=True
    )
    profile_name = serializers.CharField(source='profile_object.__str__', read_only=True)
    content_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        source='content_type',
        write_only=True
    )

    class Meta:
        model = IDCard
        fields = [
            'id', 'institution', 'institution_id',
            'role', 'user', 'user_id',
            'template_id', 'template',
            'content_type_id', 'object_id', 'profile_name',
            'unique_id', 'full_name', 'photo',
            'qr_code_image', 'barcode_image', 'class_or_department',
            'issued_on', 'expiry_date', 'is_active', 'revoked', 'reason_revoked',
            'digital_only', 'printed', 'last_printed_on'
        ]
        read_only_fields = ['qr_code_image', 'barcode_image', 'last_printed_on']


class IDCardAuditLogSerializer(serializers.ModelSerializer):
    id_card_str = serializers.CharField(source='id_card.__str__', read_only=True)
    performed_by = UserSerializer(read_only=True)
    performed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=IDCardAuditLog._meta.get_field('performed_by').related_model.objects.all(),
        source='performed_by',
        write_only=True
    )

    class Meta:
        model = IDCardAuditLog
        fields = [
            'id', 'id_card', 'id_card_str',
            'action', 'performed_by', 'performed_by_id',
            'timestamp', 'notes'
        ]
        read_only_fields = ['timestamp']


class IDCardReissueRequestSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    requester_id = serializers.PrimaryKeyRelatedField(
        queryset=IDCardReissueRequest._meta.get_field('requester').related_model.objects.all(),
        source='requester',
        write_only=True
    )
    handled_by = UserSerializer(read_only=True)
    handled_by_id = serializers.PrimaryKeyRelatedField(
        queryset=IDCardReissueRequest._meta.get_field('handled_by').related_model.objects.all(),
        source='handled_by',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = IDCardReissueRequest
        fields = [
            'id', 'requester', 'requester_id',
            'reason', 'approved', 'handled_by', 'handled_by_id',
            'approved_on', 'created_on'
        ]
        read_only_fields = ['approved_on', 'created_on']


class DigitalIDTokenSerializer(serializers.ModelSerializer):
    id_card = IDCardSerializer(read_only=True)
    id_card_id = serializers.PrimaryKeyRelatedField(
        queryset=DigitalIDToken._meta.get_field('id_card').related_model.objects.all(),
        source='id_card',
        write_only=True
    )

    class Meta:
        model = DigitalIDToken
        fields = ['id', 'id_card', 'id_card_id', 'token', 'valid_until', 'created_at']
        read_only_fields = ['token', 'created_at']
