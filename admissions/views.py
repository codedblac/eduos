from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from .models import (
    AdmissionSession, Applicant, AdmissionDocument, EntranceExam,
    AdmissionOffer, AdmissionComment
)
from .serializers import (
    AdmissionSessionSerializer, ApplicantSerializer, AdmissionDocumentSerializer,
    EntranceExamSerializer, AdmissionOfferSerializer, AdmissionCommentSerializer
)
from .permissions import IsStaffOrReadOnly, CanManageAdmission
from .filters import (
    AdmissionSessionFilter, ApplicantFilter,
    EntranceExamFilter, AdmissionOfferFilter
)
from . import analytics, ai


class AdmissionSessionViewSet(viewsets.ModelViewSet):
    queryset = AdmissionSession.objects.all()
    serializer_class = AdmissionSessionSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdmissionSessionFilter

    @action(detail=True, methods=['get'], url_path='analytics', permission_classes=[IsAuthenticated])
    def session_analytics(self, request, pk=None):
        data = analytics.get_session_based_statistics(pk)
        return Response(data)


class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ApplicantFilter

    @action(detail=True, methods=['get'], url_path='ai-recommendation')
    def ai_recommendation(self, request, pk=None):
        applicant = self.get_object()
        status_recommendation = ai.suggest_admission_offer(applicant)
        probability = ai.predict_success_probability(applicant)
        return Response({
            "should_offer": status_recommendation,
            "success_probability": probability
        })

    @action(detail=True, methods=['get'], url_path='generate-offer-letter')
    def generate_offer_letter(self, request, pk=None):
        applicant = self.get_object()
        file_obj = ai.generate_offer_letter(applicant)
        return Response({
            "message": "Offer letter generated.",
            "filename": file_obj.name
        })

    @action(detail=False, methods=['get'], url_path='special-flags')
    def special_flags(self, request):
        flagged = analytics.get_special_attention_flags()
        serializer = self.get_serializer(flagged, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='top-performers')
    def top_performers(self, request):
        top = analytics.get_top_performing_applicants()
        serializer = EntranceExamSerializer(top, many=True)
        return Response(serializer.data)


class AdmissionDocumentViewSet(viewsets.ModelViewSet):
    queryset = AdmissionDocument.objects.all()
    serializer_class = AdmissionDocumentSerializer
    permission_classes = [IsAuthenticated]


class EntranceExamViewSet(viewsets.ModelViewSet):
    queryset = EntranceExam.objects.all()
    serializer_class = EntranceExamSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EntranceExamFilter


class AdmissionOfferViewSet(viewsets.ModelViewSet):
    queryset = AdmissionOffer.objects.all()
    serializer_class = AdmissionOfferSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdmissionOfferFilter

    @action(detail=False, methods=['get'], url_path='notify-all', permission_classes=[CanManageAdmission])
    def notify_all(self, request):
        from .tasks import send_bulk_offer_notifications
        send_bulk_offer_notifications.delay()
        return Response({"message": "Bulk offer notifications task dispatched."})


class AdmissionCommentViewSet(viewsets.ModelViewSet):
    queryset = AdmissionComment.objects.all()
    serializer_class = AdmissionCommentSerializer
    permission_classes = [IsAuthenticated]


class AdmissionAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        data = {
            "summary": analytics.get_admission_summary(),
            "gender_distribution": analytics.get_gender_distribution(),
            "disability_stats": analytics.get_disability_statistics(),
            "orphan_status_stats": analytics.get_orphan_status_statistics(),
            "talents": analytics.get_talents_distribution(),
            "by_class_level": analytics.get_applicants_by_class_level(),
            "average_scores": analytics.get_average_entrance_scores(),
            "application_trends": analytics.get_application_trends_over_time(),
            "geographical_distribution": analytics.get_geographical_distribution(),
            "status_by_gender": analytics.get_status_by_gender(),
            "per_session": analytics.get_admission_session_summary(),
        }
        return Response(data)
