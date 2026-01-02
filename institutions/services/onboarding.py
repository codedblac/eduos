from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail

from rest_framework import views, status
from rest_framework.response import Response

User = get_user_model()


class OnboardingService:

    # --------------------------------------------------------
    # Generate unique institution code
    # --------------------------------------------------------
    @staticmethod
    def generate_institution_code():
        return f"SCH-{get_random_string(6).upper()}"

    # --------------------------------------------------------
    # Main onboarding process
    # --------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def onboard_institution(
        *,
        school_name: str,
        email: str,
        phone: str = None,
        county: str = "",
        country: str = "",
        sub_county: str = "",
        ward: str = "",
        village: str = "",
        institution_type: str = "OTHER",
        school_type: str = "OTHER",
        plan_name: str = "basic",
        custom_module_ids: list = None,
        admin_password: str = None,
        reg_request=None
    ):
        """
        Creates an institution + admin + billing + modules + permissions.
        """

        # Lazy imports
        from modules.models import Plan, SystemModule, ModulePermission
        from institutions.models import Institution, SchoolAccount, SchoolRegistrationRequest

        # --------------------------------------------------
        # 1️⃣ Retrieve plan OR fallback gracefully
        # --------------------------------------------------
        plan = Plan.objects.filter(name__iexact=plan_name).first()

        if not plan:
            # fallback to first plan
            plan = Plan.objects.first()

        if not plan:
            raise Exception("No plans defined in the system.")

        # --------------------------------------------------
        # 2️⃣ Create Institution
        # --------------------------------------------------
        institution = Institution.objects.create(
            name=school_name,
            code=OnboardingService.generate_institution_code(),
            country=country,
            county=county,
            sub_county=sub_county,
            ward=ward,
            village=village,
            phone=phone,
            email=email,
            institution_type=institution_type,
            school_type=school_type,
            plan=plan,
        )

        # --------------------------------------------------
        # 3️⃣ Create default billing account
        # --------------------------------------------------
        SchoolAccount.objects.create(
            institution=institution,
            account_name=f"{institution.name} Main Account",
            account_number=get_random_string(10).upper(),
            payment_type=SchoolAccount.BANK,
            is_default=True,
        )

        # --------------------------------------------------
        # 4️⃣ Determine modules based on plan or custom
        # --------------------------------------------------
        if plan.is_custom:
            # user MUST choose modules
            if custom_module_ids:
                modules = SystemModule.objects.filter(id__in=custom_module_ids)
            else:
                # fallback → only default modules
                modules = SystemModule.objects.filter(is_default=True)
        else:
            # fixed plan modules
            modules = plan.modules.all()

        modules = list(modules)

        # --------------------------------------------------
        # 5️⃣ Create Institution Admin
        # --------------------------------------------------
        if admin_password and str(admin_password).strip():
            temp_password = admin_password.strip()
        else:
            temp_password = get_random_string(12)
        
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            raise Exception(f"User with email {email} already exists.")
        
        admin_user = User.objects.create_user(
            email=email,
            first_name=school_name,
            last_name="Admin",
            primary_role=User.Role.INSTITUTION_ADMIN,
            institution=institution,
            password=temp_password,
            is_staff=True
        )

        # --------------------------------------------------
        # 6️⃣ Assign modules + permissions
        # --------------------------------------------------
        admin_user.modules.set(modules)

        # Assign role-based permissions
        module_permissions = ModulePermission.objects.filter(module__in=modules)
        admin_user.module_permissions.set(module_permissions)

        # Add Django groups if linked
        for module in modules:
            if module.linked_group:
                admin_user.groups.add(module.linked_group)

        admin_user.save()

        # --------------------------------------------------
        # 7️⃣ Link institution admin
        # --------------------------------------------------
        institution.admin_user = admin_user
        institution.save()

        # --------------------------------------------------
        # 8️⃣ If approved from registration workflow
        # --------------------------------------------------
        if reg_request:
            reg_request.approved = True
            reg_request.approved_at = timezone.now()
            reg_request.admin_created = True
            reg_request.institution = institution
            reg_request.save()

        # --------------------------------------------------
        # 9️⃣ Email admin
        # --------------------------------------------------
        send_mail(
            subject="Welcome to EduOS — Your Institution is Ready!",
            message=(
                f"Hi {admin_user.first_name},\n\n"
                f"Your institution '{institution.name}' has been onboarded.\n\n"
                f"Login:\n"
                f"Email: {admin_user.email}\n"
                f"Password: {temp_password}\n\n"
                "Please change your password after login.\n\n"
                "Thank you for choosing EduOS."
            ),
            from_email="no-reply@eduos.com",
            recipient_list=[admin_user.email],
            fail_silently=True,
        )

        # --------------------------------------------------
        #  🔟 Response summary to frontend success screen
        # --------------------------------------------------
        return {
            "institution_id": institution.id,
            "institution_code": institution.code,
            "admin_email": admin_user.email,
            "plan": plan.name,
            "modules_assigned": [m.name for m in modules],
            "temp_password": temp_password,
        }


# =========================================================
# DRF API View
# =========================================================
class OnboardInstitutionView(views.APIView):
    """
    API endpoint used by frontend onboarding wizard
    """

    def post(self, request):
        data = request.data

        summary = OnboardingService.onboard_institution(
            school_name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            county=data.get("county"),
            country=data.get("country"),
            sub_county=data.get("sub_county"),
            ward=data.get("ward"),
            village=data.get("village"),
            institution_type=data.get("institution_type", "OTHER"),
            school_type=data.get("school_type", "OTHER"),
            plan_name=data.get("default_package", "basic"),
            custom_module_ids=data.get("module_ids") or None,
            admin_password=data.get("admin_password"),
        )

        return Response(summary, status=status.HTTP_201_CREATED)
