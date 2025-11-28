from rest_framework import generics, views, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

from institutions.models import (
    Institution,
    SchoolAccount,
    SchoolRegistrationRequest
)
from institutions.serializers import (
    InstitutionSerializer,
    InstitutionCreateUpdateSerializer,
    SchoolAccountSerializer,
    SchoolAccountCreateUpdateSerializer,
    SchoolRegistrationRequestSerializer,
    SchoolRegistrationRequestCreateSerializer
)
from institutions.permissions import IsSuperAdminOrReadOnly, IsInstitutionAdminOrReadOnly
from institutions.filters import InstitutionFilter
from institutions.analytics import InstitutionAnalytics
from institutions.ai import InstitutionAIEngine

User = get_user_model()


# =============================
# 📝 School Registration Requests
# =============================

class SchoolRegistrationRequestListView(generics.ListAPIView):
    queryset = SchoolRegistrationRequest.objects.all()
    serializer_class = SchoolRegistrationRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrReadOnly]


class SchoolRegistrationRequestCreateView(generics.CreateAPIView):
    queryset = SchoolRegistrationRequest.objects.all()
    serializer_class = SchoolRegistrationRequestCreateSerializer
    permission_classes = [permissions.AllowAny]


class SchoolRegistrationRequestApproveView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrReadOnly]

    def post(self, request, pk):
        req_obj = get_object_or_404(SchoolRegistrationRequest, pk=pk)

        if req_obj.approved:
            return Response({"detail": "Request already approved."}, status=status.HTTP_400_BAD_REQUEST)

        # Create Institution
        institution = Institution.objects.create(
            name=req_obj.school_name,
            code=req_obj.code,
            country=req_obj.country,
            county=req_obj.county,
            sub_county=req_obj.sub_county,
            ward=req_obj.ward,
            village=req_obj.village,
            institution_type=req_obj.institution_type,
            school_type=req_obj.school_type
        )

        # Create Institution Admin User
        temp_password = User.objects.make_random_password()
        admin_user = User.objects.create_user(
            username=f"{req_obj.code}_admin",
            email=req_obj.email,
            password=temp_password,
            primary_role='ADMIN',
            institution=institution,
            is_active=True
        )

        # Mark request approved
        req_obj.approved = True
        req_obj.approved_at = timezone.now()
        req_obj.admin_created = True
        req_obj.save()

        return Response({
            "detail": "School registration approved.",
            "institution_id": str(institution.id),
            "admin_username": admin_user.username,
            "admin_temp_password": temp_password  # Dev only; prod: send via email
        }, status=status.HTTP_201_CREATED)


# =============================
# 🏫 Institution Views
# =============================

class InstitutionListView(generics.ListAPIView):
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InstitutionFilter

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'SUPER_ADMIN':
            return Institution.objects.all()
        elif getattr(user, 'institution', None):
            return Institution.objects.filter(id=user.institution.id)
        return Institution.objects.none()


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
        user = self.request.user
        if getattr(user, 'role', None) != 'SUPER_ADMIN' and user.institution.id != uuid.UUID(institution_id):
            raise PermissionDenied("Cannot access other institutions' accounts.")
        return SchoolAccount.objects.filter(institution_id=institution_id)

    def get_serializer_class(self):
        return SchoolAccountCreateUpdateSerializer if self.request.method == 'POST' else SchoolAccountSerializer

    def perform_create(self, serializer):
        institution_id = self.kwargs.get('institution_id')
        institution = get_object_or_404(Institution, id=institution_id)
        serializer.save(institution=institution)


class SchoolAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]

    def get_queryset(self):
        institution_id = self.kwargs.get('institution_id')
        user = self.request.user
        if getattr(user, 'role', None) != 'SUPER_ADMIN' and user.institution.id != uuid.UUID(institution_id):
            raise PermissionDenied("Cannot access other institutions' accounts.")
        return SchoolAccount.objects.filter(institution_id=institution_id)

    def get_serializer_class(self):
        return SchoolAccountCreateUpdateSerializer if self.request.method in ['PUT', 'PATCH'] else SchoolAccountSerializer


# =============================
# 🔄 Logged-in User Institution
# =============================

class MyInstitutionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.institution:
            return Response({"detail": "No institution associated."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InstitutionSerializer(request.user.institution)
        return Response(serializer.data)


# =============================
# 🤖 AI Recommendations
# =============================

class InstitutionAIRecommendationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Institution.objects.all()
        if getattr(request.user, 'institution', None):
            queryset = queryset.filter(id=request.user.institution.id)
        ai_engine = InstitutionAIEngine(queryset)
        recommendations = ai_engine.ai_dashboard_summary()
        return Response(recommendations)


# =============================
# 📊 Analytics Overview
# =============================

class InstitutionAnalyticsOverviewView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = Institution.objects.all()
        if getattr(user, 'role', None) != 'SUPER_ADMIN' and getattr(user, 'institution', None):
            queryset = queryset.filter(id=user.institution.id)

        analytics = InstitutionAnalytics(queryset)
        data = {
            "total_institutions": analytics.total_institutions(),
            "institutions_by_type": list(analytics.institutions_by_type()),
            "growth_by_year": list(analytics.growth_by_year()),
            "recent_institutions": [
                {"id": str(inst.id), "name": inst.name, "created_at": inst.created_at}
                for inst in analytics.recent_institutions()
            ],
            "location_matrix": analytics.get_location_matrix()
        }
        return Response(data)
