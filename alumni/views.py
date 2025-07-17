from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    AlumniProfile, AlumniEvent, AlumniEventRegistration,
    AlumniDonation, AlumniMentorship, AlumniAchievement,
    AlumniNotification, AlumniFeedback, AlumniMembership,
    AlumniEmployment, AlumniVolunteer
)
from .serializers import (
    AlumniProfileSerializer, AlumniEventSerializer, AlumniEventRegistrationSerializer,
    AlumniDonationSerializer, AlumniMentorshipSerializer, AlumniAchievementSerializer,
    AlumniNotificationSerializer, AlumniFeedbackSerializer, AlumniMembershipSerializer,
    AlumniEmploymentSerializer, AlumniVolunteerSerializer
)
from .permissions import IsInstitutionStaffOrAdmin


class BaseInstitutionViewSet(viewsets.ModelViewSet):
    """
    A base viewset to ensure all objects are scoped to the institution.
    """
    permission_classes = [permissions.IsAuthenticated, IsInstitutionStaffOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class AlumniProfileViewSet(BaseInstitutionViewSet):
    queryset = AlumniProfile.objects.all()
    serializer_class = AlumniProfileSerializer
    search_fields = [
        'student__first_name', 'student__last_name', 'email',
        'profession', 'university', 'organization', 'country'
    ]
    ordering_fields = ['joined_on', 'student__user__first_name']
    filterset_fields = ['is_verified', 'country', 'university']


class AlumniEventViewSet(BaseInstitutionViewSet):
    queryset = AlumniEvent.objects.all()
    serializer_class = AlumniEventSerializer
    search_fields = ['title', 'location', 'description']
    ordering_fields = ['event_date', 'created_at']
    filterset_fields = ['event_date']


class AlumniEventRegistrationViewSet(BaseInstitutionViewSet):
    queryset = AlumniEventRegistration.objects.all()
    serializer_class = AlumniEventRegistrationSerializer
    filterset_fields = ['event', 'alumni', 'is_attended']
    ordering_fields = ['registered_on']


class AlumniDonationViewSet(BaseInstitutionViewSet):
    queryset = AlumniDonation.objects.all()
    serializer_class = AlumniDonationSerializer
    filterset_fields = ['alumni', 'purpose']
    search_fields = ['purpose', 'receipt_number']
    ordering_fields = ['donated_on', 'amount']


class AlumniMentorshipViewSet(BaseInstitutionViewSet):
    queryset = AlumniMentorship.objects.all()
    serializer_class = AlumniMentorshipSerializer
    filterset_fields = ['mentor', 'mentee', 'status']
    ordering_fields = ['start_date']


class AlumniAchievementViewSet(BaseInstitutionViewSet):
    queryset = AlumniAchievement.objects.all()
    serializer_class = AlumniAchievementSerializer
    search_fields = ['title', 'description']
    ordering_fields = ['date_achieved']
    filterset_fields = ['alumni']


class AlumniNotificationViewSet(BaseInstitutionViewSet):
    queryset = AlumniNotification.objects.all()
    serializer_class = AlumniNotificationSerializer
    filterset_fields = ['recipient', 'type', 'is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['sent_on']


class AlumniFeedbackViewSet(BaseInstitutionViewSet):
    queryset = AlumniFeedback.objects.all()
    serializer_class = AlumniFeedbackSerializer
    filterset_fields = ['alumni', 'responded']
    ordering_fields = ['submitted_on']


class AlumniMembershipViewSet(BaseInstitutionViewSet):
    queryset = AlumniMembership.objects.all()
    serializer_class = AlumniMembershipSerializer
    search_fields = ['membership_number']
    filterset_fields = ['is_active_member']
    ordering_fields = ['membership_paid_on', 'next_due_date']


class AlumniEmploymentViewSet(BaseInstitutionViewSet):
    queryset = AlumniEmployment.objects.all()
    serializer_class = AlumniEmploymentSerializer
    filterset_fields = ['alumni', 'currently_employed', 'industry']
    search_fields = ['company_name', 'position', 'industry']
    ordering_fields = ['start_date', 'end_date']


class AlumniVolunteerViewSet(BaseInstitutionViewSet):
    queryset = AlumniVolunteer.objects.all()
    serializer_class = AlumniVolunteerSerializer
    search_fields = ['area_of_interest', 'availability']
    ordering_fields = ['registered_on']
    filterset_fields = ['area_of_interest']
