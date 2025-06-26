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
from .permissions import IsInstitutionAdminOrReadOnly


class BaseInstitutionViewSet(viewsets.ModelViewSet):
    """
    A base viewset to ensure all objects are scoped to the institution.
    """
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        return self.queryset.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)


class AlumniProfileViewSet(BaseInstitutionViewSet):
    queryset = AlumniProfile.objects.all()
    serializer_class = AlumniProfileSerializer
    search_fields = ['student__first_name', 'student__last_name', 'email', 'profession', 'university']


class AlumniEventViewSet(BaseInstitutionViewSet):
    queryset = AlumniEvent.objects.all()
    serializer_class = AlumniEventSerializer
    search_fields = ['title', 'location']
    ordering_fields = ['event_date']


class AlumniEventRegistrationViewSet(BaseInstitutionViewSet):
    queryset = AlumniEventRegistration.objects.all()
    serializer_class = AlumniEventRegistrationSerializer
    filterset_fields = ['event', 'alumni', 'is_attended']


class AlumniDonationViewSet(BaseInstitutionViewSet):
    queryset = AlumniDonation.objects.all()
    serializer_class = AlumniDonationSerializer
    filterset_fields = ['alumni']
    search_fields = ['purpose']


class AlumniMentorshipViewSet(BaseInstitutionViewSet):
    queryset = AlumniMentorship.objects.all()
    serializer_class = AlumniMentorshipSerializer
    filterset_fields = ['mentor', 'mentee', 'status']


class AlumniAchievementViewSet(BaseInstitutionViewSet):
    queryset = AlumniAchievement.objects.all()
    serializer_class = AlumniAchievementSerializer
    search_fields = ['title', 'description']


class AlumniNotificationViewSet(BaseInstitutionViewSet):
    queryset = AlumniNotification.objects.all()
    serializer_class = AlumniNotificationSerializer
    filterset_fields = ['recipient', 'type']
    search_fields = ['title', 'message']


class AlumniFeedbackViewSet(BaseInstitutionViewSet):
    queryset = AlumniFeedback.objects.all()
    serializer_class = AlumniFeedbackSerializer
    filterset_fields = ['alumni', 'responded']


class AlumniMembershipViewSet(BaseInstitutionViewSet):
    queryset = AlumniMembership.objects.all()
    serializer_class = AlumniMembershipSerializer
    search_fields = ['membership_number']


class AlumniEmploymentViewSet(BaseInstitutionViewSet):
    queryset = AlumniEmployment.objects.all()
    serializer_class = AlumniEmploymentSerializer
    filterset_fields = ['alumni', 'currently_employed']
    search_fields = ['company_name', 'position']


class AlumniVolunteerViewSet(BaseInstitutionViewSet):
    queryset = AlumniVolunteer.objects.all()
    serializer_class = AlumniVolunteerSerializer
    search_fields = ['area_of_interest', 'availability']
