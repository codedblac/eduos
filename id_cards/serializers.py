from rest_framework import serializers
from .models import IDCardTemplate, IDCard, IDCardAuditLog, IDCardReissueRequest, DigitalIDToken


class IDCardTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDCardTemplate
        fields = '__all__'


class IDCardSerializer(serializers.ModelSerializer):
    profile_name = serializers.CharField(source='profile_object.__str__', read_only=True)
    
    class Meta:
        model = IDCard
        fields = [
            'id', 'institution', 'role', 'user', 'template', 'content_type', 'object_id', 'profile_name',
            'unique_id', 'full_name', 'photo', 'qr_code_image', 'barcode_image', 'class_or_department',
            'issued_on', 'expiry_date', 'is_active', 'revoked', 'reason_revoked',
            'digital_only', 'printed', 'last_printed_on'
        ]
        read_only_fields = ['qr_code_image', 'barcode_image', 'last_printed_on']


class IDCardAuditLogSerializer(serializers.ModelSerializer):
    id_card_str = serializers.CharField(source='id_card.__str__', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model = IDCardAuditLog
        fields = ['id', 'id_card', 'id_card_str', 'action', 'performed_by', 'performed_by_name', 'timestamp', 'notes']


class IDCardReissueRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    handler_name = serializers.CharField(source='handled_by.get_full_name', read_only=True)

    class Meta:
        model = IDCardReissueRequest
        fields = [
            'id', 'requester', 'requester_name', 'reason', 'approved', 'handled_by',
            'handler_name', 'approved_on', 'created_on'
        ]
        read_only_fields = ['approved_on', 'created_on']


class DigitalIDTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalIDToken
        fields = ['id', 'id_card', 'token', 'valid_until', 'created_at']
