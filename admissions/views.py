from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from admissions.ai import recommend_admission_status
from admissions.models import Applicant
from admissions.analytics import get_admission_summary 
from rest_framework import permissions, status
from students.models import Student  
from .models import (
    AdmissionSession, Applicant, AdmissionDocument, EntranceExam,
    AdmissionOffer, AdmissionComment
)
from .serializers import (
    AdmissionSessionSerializer, ApplicantSerializer, AdmissionDocumentSerializer,
    EntranceExamSerializer, AdmissionOfferSerializer, AdmissionCommentSerializer
)
from .permissions import IsOwnerOrReadOnly, CanManageAdmission
from .filters import (
    AdmissionSessionFilter, ApplicantFilter,
    EntranceExamFilter, AdmissionOfferFilter
)
from . import analytics, ai


class AdmissionSessionViewSet(viewsets.ModelViewSet):
    queryset = AdmissionSession.objects.all()
    serializer_class = AdmissionSessionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
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
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EntranceExamFilter


class AdmissionOfferViewSet(viewsets.ModelViewSet):
    queryset = AdmissionOffer.objects.all()
    serializer_class = AdmissionOfferSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
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


class AIPlacementSuggestionAPIView(APIView):
    def post(self, request):
        # TODO: Replace with real AI logic
        data = request.data
        suggested_class = "Grade 5"  # Placeholder logic
        return Response({"suggested_class": suggested_class}, status=status.HTTP_200_OK)
    

class RecommendAdmissionStatusAPIView(APIView):
    def get(self, request, pk):
        try:
            application = Applicant.objects.get(pk=pk)
        except Applicant.DoesNotExist:
            return Response({"error": "Application not found."}, status=404)

        # Actual recommendation logic using your AI or rule-based system
        recommended_status = recommend_admission_status(application)

        return Response({
            "applicant_id": application.id,
            "recommended_status": recommended_status
        }, status=200)
        
        
class AdmissionAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        summary = get_admission_summary()
        return Response(summary, status=status.HTTP_200_OK)
    
    
class GenerateOfferLetterAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        application = get_object_or_404(Applicant, pk=pk)
        
        # TODO: Replace with real letter generation logic
        # For now just simulating data
        offer_data = {
            "applicant": str(application.applicant),
            "program": str(application.program_applied),
            "status": application.status,
            "message": "Offer letter generated successfully."
        }

        # You can later replace this with PDF generation and file response
        return Response(offer_data, status=status.HTTP_200_OK)
    
    
class EnrollApplicantAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        application = get_object_or_404(Applicant, pk=pk)

        if application.status != "accepted":
            return Response({"detail": "Only accepted applicants can be enrolled."}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Replace with actual enrollment logic (e.g. create StudentProfile, ClassAssignment, etc.)
        application.status = "enrolled"
        application.save()

        return Response({"message": "Applicant successfully enrolled."}, status=status.HTTP_200_OK)
    
    
class GenerateStudentIDAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        application = get_object_or_404(Applicant, pk=pk)

        if not application.student_id:
            # Example logic to generate ID — you can customize this
            application.student_id = f"S{str(application.id).zfill(6)}"
            application.save()

        return Response({
            "message": "Student ID generated successfully.",
            "student_id": application.student_id
        }, status=status.HTTP_200_OK)