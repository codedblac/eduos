from rest_framework import serializers
from .models import (
    AdmissionSession,
    Applicant,
    AdmissionDocument,
    EntranceExam,
    AdmissionOffer,
    AdmissionComment
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


class ApplicantSerializer(serializers.ModelSerializer):
    documents = AdmissionDocumentSerializer(many=True, read_only=True)
    comments = AdmissionCommentSerializer(many=True, read_only=True)
    entranceexam_set = EntranceExamSerializer(many=True, read_only=True)
    admissionoffer_set = AdmissionOfferSerializer(many=True, read_only=True)

    class Meta:
        model = Applicant
        fields = '__all__'


class ApplicantStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = ['application_status']


class EnrollApplicantSerializer(serializers.Serializer):
    applicant_id = serializers.IntegerField()
    target_class_level_id = serializers.IntegerField()
    hostel_preference = serializers.CharField(required=False)
    allocate_hostel = serializers.BooleanField(default=False)
