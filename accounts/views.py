from rest_framework import generics, status, permissions, views
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from django.conf import settings

from accounts.models import CustomUser
from accounts.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserMinimalSerializer,
    PublicUserSignupSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,  
    PasswordResetConfirmSerializer,
)
from accounts.permissions import (
    IsSuperAdmin,
    IsInstitutionAdmin,
    IsSameInstitutionOrSuperAdmin,
)
from accounts.filters import UserFilter
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()


#  Public Registration


class RegisterView(generics.CreateAPIView):
    serializer_class = PublicUserSignupSerializer
    permission_classes = [permissions.AllowAny]



#  Login (Token-based)


class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = token.user
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        })



#  User Management


class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.select_related("institution").all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_serializer_class(self):
        return UserCreateSerializer if self.request.method == "POST" else UserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsInstitutionAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == CustomUser.Role.SUPER_ADMIN:
            return self.queryset
        elif user.institution:
            return self.queryset.filter(institution=user.institution)
        return CustomUser.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in [CustomUser.Role.SUPER_ADMIN, CustomUser.Role.ADMIN]:
            raise PermissionDenied("You do not have permission to create users.")
        serializer.save(institution=user.institution)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.select_related("institution").all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameInstitutionOrSuperAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == CustomUser.Role.SUPER_ADMIN:
            return self.queryset
        elif user.institution:
            return self.queryset.filter(institution=user.institution)
        return CustomUser.objects.none()



#  Profile (Me)


class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



#  Account Switcher


class SwitchAccountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get("target_user_id")
        if not target_user_id:
            return Response({"error": "target_user_id is required"}, status=400)

        target_user = get_object_or_404(CustomUser, id=target_user_id)
        # TODO: Add relationship check
        return Response(UserMinimalSerializer(target_user).data)



#  Role Listing


class UserRolesView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        roles = [{"value": r[0], "label": r[1]} for r in CustomUser.Role.choices]
        return Response(roles)



#  Change Password


class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Password changed successfully."})



#  Forgot Password (Reset Request)


class ForgotPasswordView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)  # ✅ Fixed
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = get_object_or_404(User, email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        send_mail(
            "Reset your EduOS password",
            f"Use this link to reset your password:\n\n{reset_url}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        return Response({"detail": "Reset email sent."})



#  Password Reset Confirm


class PasswordResetConfirmView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid reset link."}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password has been reset successfully."})
