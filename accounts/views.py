from rest_framework import generics, permissions, views
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
from rest_framework.authtoken.views import ObtainAuthToken
from accounts.models import CustomUser
from accounts.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    PublicUserSignupSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailTokenObtainPairSerializer,
)
from accounts.permissions import (
    IsSuperAdmin,
    IsInstitutionAdmin,
    IsSameInstitutionOrSuperAdmin,
)
from accounts.filters import UserFilter
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


# -------------------------------------------------
#  Create Institution Admin
# -------------------------------------------------
class CreateInstitutionAdminView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]

    def perform_create(self, serializer):
        serializer.save(
            primary_role=CustomUser.Role.INSTITUTION_ADMIN,
            institution=self.request.user.institution
        )


# -------------------------------------------------
#  Public Registration
# -------------------------------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = PublicUserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save(primary_role=CustomUser.Role.PUBLIC_LEARNER)


# -------------------------------------------------
#  Login (JWT)
# -------------------------------------------------
class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = token.user
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        })


# -------------------------------------------------
#  User List & Create
# -------------------------------------------------
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

        # Optional: Add modules if provided
        modules = self.request.data.get("modules", [])
        if modules:
            from accounts.models import SystemModule
            module_objects = SystemModule.objects.filter(name__in=modules)
            instance.modules.set(module_objects)
            instance.save()


# -------------------------------------------------
#  User Detail
# -------------------------------------------------
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.select_related("institution").all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameInstitutionOrSuperAdmin]


# -------------------------------------------------
#  Profile (Me)
# -------------------------------------------------
class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserDetailSerializer(request.user).data)


# -------------------------------------------------
#  Role Listing (from TextChoices Enum)
# -------------------------------------------------
class UserRolesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        roles = [{"name": r[0], "label": r[1]} for r in CustomUser.Role.choices]
        return Response(roles)


# -------------------------------------------------
#  Change Password
# -------------------------------------------------
class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response({"detail": "Password changed successfully."})


# -------------------------------------------------
#  Forgot Password
# -------------------------------------------------
class ForgotPasswordView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, email=serializer.validated_data["email"])
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        user.email_user("Reset your EduOS password", f"Use this link to reset your password:\n{reset_url}")

        return Response({"detail": "Reset email sent."})


# -------------------------------------------------
#  Confirm Reset Password
# -------------------------------------------------
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



class SwitchAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({"detail": "Switch account feature not implemented yet."}, status=501)
