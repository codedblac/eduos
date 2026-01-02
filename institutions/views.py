# institutions/views.py

from rest_framework import generics, views, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from uuid import UUID
from rest_framework.decorators import action
from institutions.models import InstitutionStatus


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
    SchoolRegistrationRequestCreateSerializer,
    InstitutionOnboardingSerializer
)
from institutions.permissions import IsSuperAdminOrReadOnly, IsInstitutionAdminOrReadOnly
from institutions.filters import InstitutionFilter
from institutions.analytics import InstitutionAnalytics
from institutions.ai import InstitutionAIEngine
from modules.models import SystemModule, SchoolModule
from accounts.models import CustomUser

User = get_user_model()

def block_if_institution_suspended(user):
    if user.institution and user.institution.status == InstitutionStatus.SUSPENDED:
        raise PermissionDenied("This institution is suspended. Contact support.")


# =====================================================================
# 📌 1. School Registration Request Views
# =====================================================================

class SchoolRegistrationRequestListView(generics.ListAPIView):
    queryset = SchoolRegistrationRequest.objects.all()
    serializer_class = SchoolRegistrationRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrReadOnly]


class SchoolRegistrationRequestCreateView(generics.CreateAPIView):
    queryset = SchoolRegistrationRequest.objects.all()
    serializer_class = SchoolRegistrationRequestCreateSerializer
    permission_classes = [permissions.AllowAny]


class SchoolRegistrationRequestApproveView(views.APIView):
    """
    Approves a manual registration request (admin-driven onboarding)
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrReadOnly]

    def post(self, request, pk):
        req_obj = get_object_or_404(SchoolRegistrationRequest, pk=pk)

        if req_obj.approved:
            return Response({"detail": "Request already approved."}, status=status.HTTP_400_BAD_REQUEST)

        # -----------------------------------------
        # 1️⃣ Create Institution
        # -----------------------------------------
        institution = Institution.objects.create(
            name=req_obj.school_name,
            code=req_obj.code,
            country=req_obj.country,
            county=req_obj.county,
            sub_county=req_obj.sub_county,
            ward=req_obj.ward,
            village=req_obj.village,
            institution_type=req_obj.institution_type,
            school_type=req_obj.school_type,
            email=req_obj.email,
            phone=req_obj.phone
        )

        # -----------------------------------------
        # 2️⃣ Create Institution Admin User
        # -----------------------------------------
        temp_password = User.objects.make_random_password()
        admin_user = User.objects.create_user(
            email=req_obj.email,
            password=temp_password,
            first_name="Admin",
            last_name=institution.name,
            primary_role=CustomUser.Roles.INSTITUTION_ADMIN,
            institution=institution,
            is_staff=True,
            is_superuser=False
        )

        # -----------------------------------------
        # 3️⃣ Assign default modules
        # -----------------------------------------
        default_modules = SystemModule.objects.filter(is_default=True)
        assigned_modules = []

        for module in default_modules:
            sm, _ = SchoolModule.objects.get_or_create(
                institution=institution,
                module=module
            )
            assigned_modules.append(sm)

            admin_user.modules.add(module)

            # Add default permissions
            if module.linked_group:
                admin_user.groups.add(module.linked_group)

        admin_user.save()

        # -----------------------------------------
        # 4️⃣ Mark request as approved
        # -----------------------------------------
        req_obj.approved = True
        req_obj.approved_at = timezone.now()
        req_obj.admin_created = True
        req_obj.save()

        # -----------------------------------------
        # 5️⃣ Send login email
        # -----------------------------------------
        send_mail(
            subject=f"Welcome to {institution.name}",
            message=(
                f"Hello,\n\n"
                f"Your institution '{institution.name}' has been approved.\n\n"
                f"Login URL: {settings.FRONTEND_LOGIN_URL}\n"
                f"Email: {admin_user.email}\n"
                f"Temporary Password: {temp_password}\n\n"
                f"Please change your password on first login."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_user.email],
            fail_silently=False
        )

        # -----------------------------------------
        return Response({
            "detail": "Institution successfully onboarded.",
            "institution": {"id": str(institution.id), "name": institution.name},
            "admin": {"email": admin_user.email},
            "modules": [sm.module.name for sm in assigned_modules],
        }, status=status.HTTP_201_CREATED)


# =====================================================================
# 🚀 2. Automated Full Institution Onboarding (Self-service or Admin)
# =====================================================================

class OnboardInstitutionView(generics.GenericAPIView):
    """
    Full onboarding endpoint:
    - Creates institution
    - Creates institution admin
    - Assigns modules (package-based or custom)
    - Sends email with credentials
    """

    serializer_class = InstitutionOnboardingSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # ----------------------------------------------------
        # Create Institution
        # ----------------------------------------------------
        institution = Institution.objects.create(
            name=data["name"],
            code=data["code"],
            country=data["country"],
            county=data["county"],
            sub_county=data.get("sub_county"),
            ward=data.get("ward"),
            village=data.get("village"),
            address=data.get("address"),
            phone=data.get("phone"),
            email=data.get("email"),
            website=data.get("website"),
            primary_color=data.get("primary_color"),
            secondary_color=data.get("secondary_color"),
            theme_mode=data.get("theme_mode"),
            school_type=data["school_type"],
            institution_type=data["institution_type"],
            ownership=data.get("ownership"),
            funding_source=data.get("funding_source"),
            established_year=data.get("established_year"),
        )

        # ----------------------------------------------------
        # Create Institution Admin User
        # ----------------------------------------------------
        admin_password = data["password"]
        admin_user = User.objects.create_user(
            email=data["email"],
            password=admin_password,
            first_name="Admin",
            last_name=institution.name,
            primary_role=CustomUser.Roles.INSTITUTION_ADMIN,
            institution=institution,
            is_staff=True,
        )

        # ----------------------------------------------------
        # Module Assignment
        # ----------------------------------------------------
        assigned_modules = []

        if data.get("default_package") and data["default_package"] != "CUSTOM":
            # Assign default package
            package_name = data["default_package"]
            modules = SystemModule.objects.filter(package_type=package_name)
        else:
            # Custom module list
            module_ids = data.get("module_ids", [])
            modules = SystemModule.objects.filter(id__in=module_ids)

        for mod in modules:
            sm, _ = SchoolModule.objects.get_or_create(institution=institution, module=mod)
            assigned_modules.append(sm)
            admin_user.modules.add(mod)

            if mod.linked_group:
                admin_user.groups.add(mod.linked_group)

        admin_user.save()

        # ----------------------------------------------------
        # Send Credentials Email
        # ----------------------------------------------------
        send_mail(
            subject=f"Your Institution ({institution.name}) Is Ready 🎉",
            message=(
                f"Hello,\n\n"
                f"Your institution '{institution.name}' has been successfully onboarded.\n\n"
                f"Login URL: {settings.FRONTEND_LOGIN_URL}\n"
                f"Email: {admin_user.email}\n"
                f"Password: {admin_password}\n\n"
                f"Please change your password after logging in.\n\n"
                f"Welcome aboard!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_user.email],
            fail_silently=False
        )

        return Response({
            "detail": "Institution onboarded successfully.",
            "institution": InstitutionSerializer(institution).data,
            "admin": {"email": admin_user.email},
            "modules": [m.module.name for m in assigned_modules],
        }, status=status.HTTP_201_CREATED)


# =====================================================================
# 🏫 3. Institution CRUD Views
# =====================================================================

class InstitutionListView(generics.ListAPIView):
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InstitutionFilter

    def get_queryset(self):
        user = self.request.user

        if user.primary_role == CustomUser.Roles.SUPER_ADMIN:
            return Institution.objects.all()

        if user.institution:
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


# =====================================================================
# 💳 4. School Account Views
# =====================================================================

class SchoolAccountListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        institution_id = self.kwargs.get("institution_id")
        user = self.request.user

        if user.primary_role != CustomUser.Roles.SUPER_ADMIN:
            if not user.institution or user.institution.id != UUID(institution_id):
                raise PermissionDenied("Not allowed.")

        return SchoolAccount.objects.filter(institution_id=institution_id)

    def get_serializer_class(self):
        return SchoolAccountCreateUpdateSerializer if self.request.method == "POST" else SchoolAccountSerializer

    def perform_create(self, serializer):
        institution_id = self.kwargs.get("institution_id")
        institution = get_object_or_404(Institution, id=institution_id)
        serializer.save(institution=institution)


class SchoolAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]

    def get_queryset(self):
        institution_id = self.kwargs.get("institution_id")
        user = self.request.user

        if user.primary_role != CustomUser.Roles.SUPER_ADMIN:
            if not user.institution or user.institution.id != UUID(institution_id):
                raise PermissionDenied("Not allowed.")

        return SchoolAccount.objects.filter(institution_id=institution_id)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SchoolAccountCreateUpdateSerializer
        return SchoolAccountSerializer


# =====================================================================
# 🔄 5. Logged-in User Institution
# =====================================================================

class MyInstitutionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        block_if_institution_suspended(request.user)
        if not request.user.institution:
            return Response({"detail": "No institution assigned."}, status=404)
        return Response(InstitutionSerializer(request.user.institution).data)


# =====================================================================
# 🤖 6. AI Recommendations
# =====================================================================

class InstitutionAIRecommendationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        block_if_institution_suspended(request.user)

        queryset = Institution.objects.all()

        if request.user.institution:
            queryset = queryset.filter(id=request.user.institution.id)

        ai_engine = InstitutionAIEngine(queryset)
        return Response(ai_engine.ai_dashboard_summary())



# =====================================================================
# 📊 7. Analytics
# =====================================================================

class InstitutionAnalyticsOverviewView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        block_if_institution_suspended(request.user)

        user = request.user
        queryset = Institution.objects.all()

        if user.primary_role != CustomUser.Roles.SUPER_ADMIN:
            if user.institution:
                queryset = queryset.filter(id=user.institution.id)
            else:
                queryset = Institution.objects.none()

        analytics = InstitutionAnalytics(queryset)

        return Response({
            "total_institutions": analytics.total_institutions(),
            "institutions_by_type": list(analytics.institutions_by_type()),
            "growth_by_year": list(analytics.growth_by_year()),
            "recent_institutions": [
                {"id": str(inst.id), "name": inst.name, "created_at": inst.created_at}
                for inst in analytics.recent_institutions()
            ],
            "location_matrix": analytics.get_location_matrix()
        })



class InstitutionStatusUpdateView(views.APIView):
    """
    Suspend or activate an institution
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrReadOnly]

    def patch(self, request, pk):
        institution = get_object_or_404(Institution, pk=pk)

        new_status = request.data.get("status")

        if new_status not in InstitutionStatus.values:
            return Response(
                {"detail": "Invalid status value."},
                status=status.HTTP_400_BAD_REQUEST
            )

        institution.status = new_status
        institution.save(update_fields=["status"])

        return Response({
            "detail": "Institution status updated successfully.",
            "institution": InstitutionSerializer(institution).data
        })

