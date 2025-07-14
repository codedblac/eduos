from rest_framework import serializers
from .models import (
    AdmissionSession,
    Applicant,
    AdmissionDocument,
    EntranceExam,
    AdmissionOffer,
    AdmissionComment,
    AdmissionWorkflowStep,
    AdmissionAuditLog
)


class AdmissionSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionSession
        fields = '__all__'


class AdmissionDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionDocument
        fields = '__all__'


class EntranceExamSerializer(serializers.ModelSerializer):
    applicant_name = serializers.StringRelatedField(source='applicant', read_only=True)

    class Meta:
        model = EntranceExam
        fields = '__all__'


class AdmissionOfferSerializer(serializers.ModelSerializer):
    applicant_name = serializers.StringRelatedField(source='applicant', read_only=True)

    class Meta:
        model = AdmissionOffer
        fields = '__all__'


class AdmissionCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(source='author', read_only=True)

    class Meta:
        model = AdmissionComment
        fields = '__all__'


class AdmissionWorkflowStepSerializer(serializers.ModelSerializer):
    completed_by_name = serializers.StringRelatedField(source='completed_by', read_only=True)

    class Meta:
        model = AdmissionWorkflowStep
        fields = '__all__'


class AdmissionAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.StringRelatedField(source='actor', read_only=True)

    class Meta:
        model = AdmissionAuditLog
        fields = '__all__'


class ApplicantSerializer(serializers.ModelSerializer):
    documents = AdmissionDocumentSerializer(many=True, read_only=True)
    comments = AdmissionCommentSerializer(many=True, read_only=True)
    workflow_steps = AdmissionWorkflowStepSerializer(many=True, read_only=True)
    entranceexam_set = EntranceExamSerializer(many=True, read_only=True)
    admissionoffer_set = AdmissionOfferSerializer(many=True, read_only=True)

    class Meta:
        model = Applicant
        fields = '__all__'


class ApplicantCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        exclude = ['submitted_on', 'is_converted_to_student']


class ApplicantStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ['application_status']


class EnrollApplicantSerializer(serializers.Serializer):
    applicant_id = serializers.IntegerField()
    target_class_level_id = serializers.IntegerField()
    hostel_preference = serializers.CharField(required=False, allow_blank=True)
    allocate_hostel = serializers.BooleanField(default=False)
