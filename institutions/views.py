from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Institution, SchoolAccount
from .serializers import InstitutionSerializer, SchoolAccountSerializer
from .permissions import IsSuperAdmin, CanManageInstitution, CanManageSchoolAccounts
from .filters import InstitutionFilter, SchoolAccountFilter
from accounts.permissions import IsSameInstitution

# ===============================
# Institution Views
# ===============================

class InstitutionListCreateView(generics.ListCreateAPIView):
    """
    SuperAdmin can view all and create new institutions (e.g., schools).
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InstitutionFilter


class InstitutionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    SuperAdmin can view, update, or delete a specific institution.
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    lookup_field = 'pk'

# ===============================
# SchoolAccount Views
# ===============================

class SchoolAccountListCreateView(generics.ListCreateAPIView):
    """
    Admin/Bursar/Finance roles can create or view their school's payment accounts.
    """
    serializer_class = SchoolAccountSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageSchoolAccounts]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SchoolAccountFilter

    def get_queryset(self):
        institution_id = self.kwargs.get('institution_id')
        return SchoolAccount.objects.filter(institution_id=institution_id)

    def perform_create(self, serializer):
        institution_id = self.kwargs.get('institution_id')
        serializer.save(institution_id=institution_id)


class SchoolAccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Admin/Bursar/Finance roles can manage a specific payment account.
    """
    queryset = SchoolAccount.objects.all()
    serializer_class = SchoolAccountSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageSchoolAccounts]
    lookup_field = 'pk'
