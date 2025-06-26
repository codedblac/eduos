from django.shortcuts import render

# Create your views here.
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
from .permissions import IsStaffOrReadOnly
from .filters import (
    AdmissionSessionFilter, ApplicantFilter,
    EntranceExamFilter, AdmissionOfferFilter
)
from .ai import generate_offer_letter_ai, recommend_admission_status
from .analytics import get_admission_analytics


class AdmissionSessionViewSet(viewsets.ModelViewSet):
    queryset = AdmissionSession.objects.all()
    serializer_class = AdmissionSessionSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdmissionSessionFilter


class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ApplicantFilter

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def generate_offer_letter(self, request, pk=None):
        applicant = self.get_object()
        letter = generate_offer_letter_ai(applicant)
        return Response({"message": "Offer letter generated successfully", "letter": letter})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def ai_recommendation(self, request, pk=None):
        applicant = self.get_object()
        recommendation = recommend_admission_status(applicant)
        return Response({"recommended_status": recommendation})


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


class AdmissionCommentViewSet(viewsets.ModelViewSet):
    queryset = AdmissionComment.objects.all()
    serializer_class = AdmissionCommentSerializer
    permission_classes = [IsAuthenticated]


class AdmissionAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        data = get_admission_analytics()
        return Response(data)
