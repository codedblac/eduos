from rest_framework import viewsets, permissions
from .models import Guardian, GuardianStudentLink, GuardianNotification
from .serializers import GuardianSerializer, GuardianStudentLinkSerializer, GuardianNotificationSerializer

class GuardianViewSet(viewsets.ModelViewSet):
    serializer_class = GuardianSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Guardian.objects.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, institution=self.request.user.institution)


class GuardianStudentLinkViewSet(viewsets.ModelViewSet):
    serializer_class = GuardianStudentLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GuardianStudentLink.objects.filter(guardian__institution=self.request.user.institution)

    def perform_create(self, serializer):
        guardian = Guardian.objects.get(user=self.request.user)
        serializer.save(guardian=guardian)


class GuardianNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = GuardianNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GuardianNotification.objects.filter(
            institution=self.request.user.institution,
            guardian__user=self.request.user
        )

    def perform_create(self, serializer):
        guardian = Guardian.objects.get(user=self.request.user)
        serializer.save(guardian=guardian, institution=self.request.user.institution)
