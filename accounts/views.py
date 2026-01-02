from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import CustomUser, SystemModule, ModulePermission
from accounts.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    PublicUserSignupSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailTokenObtainPairSerializer,
    SystemModuleSerializer,
)
from accounts.permissions import (
    IsSuperAdmin,
    IsInstitutionAdmin,
    IsSameInstitutionOrSuperAdmin,
)
from accounts.filters import UserFilter

User = get_user_model()

# ---------------------------
# Module Views
# ---------------------------
class ModuleListView(generics.ListAPIView):
    queryset = SystemModule.objects.prefetch_related("permissions").all()
    serializer_class = SystemModuleSerializer
    permission_classes = [permissions.IsAuthenticated]


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SystemModule.objects.prefetch_related("permissions").all()
    serializer_class = SystemModuleSerializer
    permission_classes = [IsSuperAdmin]


# ---------------------------
# Create Institution Admin
# ---------------------------
class CreateInstitutionAdminView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [IsSuperAdmin]

    def perform_create(self, serializer):
        user = serializer.save(
            primary_role=CustomUser.Role.INSTITUTION_ADMIN,
            institution=self.request.user.institution
        )
        # Assign default modules and group permissions
        default_modules = SystemModule.objects.filter(is_default=True)
        user.modules.set(default_modules)
        for module in default_modules:
            if module.default_group:
                user.groups.add(module.default_group)
        perms = ModulePermission.objects.filter(module__in=default_modules)
        user.module_permissions.set(perms)
        user.save()


# ---------------------------
# Public Registration
# ---------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = PublicUserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(primary_role=CustomUser.Role.PUBLIC_LEARNER)
        # Assign default public modules if any
        default_modules = SystemModule.objects.filter(is_default=True)
        user.modules.set(default_modules)
        for module in default_modules:
            if module.default_group:
                user.groups.add(module.default_group)
        perms = ModulePermission.objects.filter(module__in=default_modules)
        user.module_permissions.set(perms)
        user.save()


# ---------------------------
# Login (JWT)
# ---------------------------
class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


# ---------------------------
# User List & Create
# ---------------------------
class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.select_related("institution").all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserFilter
    ordering_fields = ["first_name", "last_name", "email", "date_joined"]
    ordering = ["first_name"]

    def get_serializer_class(self):
        return UserCreateSerializer if self.request.method == "POST" else UserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsInstitutionAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.primary_role == CustomUser.Role.SUPER_ADMIN:
            return self.queryset
        if user.institution:
            return self.queryset.filter(institution=user.institution)
        return CustomUser.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.primary_role not in [
            CustomUser.Role.SUPER_ADMIN,
            CustomUser.Role.INSTITUTION_ADMIN
        ]:
            raise PermissionDenied("You do not have permission to create users.")

        primary_role = self.request.data.get("primary_role", 'STAFF')

        if primary_role not in CustomUser.Role.values:
            raise PermissionDenied(f"Invalid role '{primary_role}'.")

        instance = serializer.save(
            institution=user.institution,
            primary_role=primary_role,
        )

        # Assign modules and automatically handle group permissions
        modules = self.request.data.get("modules", [])
        if modules:
            module_objects = SystemModule.objects.filter(id__in=modules)
            instance.modules.set(module_objects)

            for module in module_objects:
                if module.default_group:
                    instance.groups.add(module.default_group)

            all_perms = ModulePermission.objects.filter(module__in=module_objects)
            instance.module_permissions.set(all_perms)

        instance.save()


# ---------------------------
# User Detail
# ---------------------------
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.select_related("institution").all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameInstitutionOrSuperAdmin]

    def perform_update(self, serializer):
        instance = serializer.save()
        modules = self.request.data.get("modules", None)
        if modules is not None:
            module_objects = SystemModule.objects.filter(id__in=modules)
            instance.modules.set(module_objects)

            for module in module_objects:
                if module.default_group:
                    instance.groups.add(module.default_group)

            all_perms = ModulePermission.objects.filter(module__in=module_objects)
            instance.module_permissions.set(all_perms)

        instance.save()


# ---------------------------
# Profile (Me)
# ---------------------------
class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserDetailSerializer(request.user).data)


# ---------------------------
# Role Listing
# ---------------------------
class UserRolesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        roles = [{"name": r[0], "label": r[1]} for r in CustomUser.Role.choices]
        return Response(roles)


# ---------------------------
# Change Password
# ---------------------------
class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response({"detail": "Password changed successfully."})


# ---------------------------
# Forgot Password
# ---------------------------
class ForgotPasswordView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, email=serializer.validated_data["email"])
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        user.email_user(
            "Reset your EduOS password",
            f"Use this link to reset your password:\n{reset_url}"
        )

        return Response({"detail": "Reset email sent."})


# ---------------------------
# Confirm Reset Password
# ---------------------------
class PasswordResetConfirmView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
        except (User.DoesNotExist, ValueError):
            return Response({"error": "Invalid reset link."}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"detail": "Password has been reset successfully."})


# ---------------------------
# Switch Account (Placeholder)
# ---------------------------
class SwitchAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({"detail": "Switch account feature not implemented yet."}, status=501)
