from rest_framework import generics, views, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from institutions.models import Institution, SchoolAccount
from institutions.serializers import (
    InstitutionSerializer,
    SchoolAccountSerializer,
)
from institutions.permissions import IsSuperAdminOrReadOnly, IsInstitutionAdminOrReadOnly
from institutions.filters import InstitutionFilter

# Try custom create/update serializers, fallback to base serializers
try:
    from institutions.serializers import InstitutionCreateUpdateSerializer
except ImportError:
    InstitutionCreateUpdateSerializer = InstitutionSerializer

try:
    from institutions.serializers import SchoolAccountCreateUpdateSerializer
except ImportError:
    SchoolAccountCreateUpdateSerializer = SchoolAccountSerializer


# =============================
# 🏫 Institution Views
# =============================

class InstitutionListView(generics.ListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InstitutionFilter


class InstitutionCreateView(generics.CreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrReadOnly]


class InstitutionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Institution.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InstitutionCreateUpdateSerializer
        return InstitutionSerializer


# =============================
# 💳 School Account Views
# =============================

class SchoolAccountListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        institution_id = self.kwargs.get('institution_id')
        return SchoolAccount.objects.filter(institution_id=institution_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SchoolAccountCreateUpdateSerializer
        return SchoolAccountSerializer

    def perform_create(self, serializer):
        institution_id = self.kwargs.get('institution_id')
        institution = get_object_or_404(Institution, id=institution_id)
        serializer.save(institution=institution)


class SchoolAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]

    def get_queryset(self):
        institution_id = self.kwargs.get('institution_id')
        return SchoolAccount.objects.filter(institution_id=institution_id)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SchoolAccountCreateUpdateSerializer
        return SchoolAccountSerializer


# =============================
# 🔄 Logged-in User Institution
# =============================

class MyInstitutionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.institution:
            return Response({"detail": "No institution associated."}, status=status.HTTP_404_NOT_FOUND)

        institution = request.user.institution
        serializer = InstitutionSerializer(institution)
        return Response(serializer.data)


# =============================
# 🤖 AI Recommendation Stub
# =============================

class InstitutionAIRecommendationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "AI-based institution recommendations will be available soon.",
            "recommended_colors": ["#0047AB", "#28a745", "#ffc107"]
        })


# =============================
# 📊 Analytics Overview Stub
# =============================

class InstitutionAnalyticsOverviewView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "total_institutions": Institution.objects.count(),
            "schools_by_type": {
                "primary": Institution.objects.filter(school_type="PRIMARY").count(),
                "secondary": Institution.objects.filter(school_type="SECONDARY").count(),
                "university": Institution.objects.filter(school_type="UNIVERSITY").count(),
            }
        })
