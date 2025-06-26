from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Institution
from .serializers import (
    UserCreateSerializer, UserDetailSerializer, UserUpdateSerializer,
    InstitutionSerializer
)
from .permissions import (
    IsSuperAdmin,
    CanManageUsers,
    IsSameInstitution,
    IsAuthenticatedAndActive
)

User = get_user_model()


# ==========================
# Custom Permission: IsSelfOrSameInstitution
# ==========================
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelfOrSameInstitution(BasePermission):
    """
    Allows update if the user is self or from same institution.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_super_admin:
            return True
        return obj == request.user or (
            hasattr(obj, 'institution') and 
            obj.institution == request.user.institution
        )


# ==========================
# JWT Login View
# ==========================
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            institution_data = (
                InstitutionSerializer(user.institution).data
                if user.institution else None
            )
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserDetailSerializer(user).data,
                "institution": institution_data
            })

        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# ==========================
# User Registration View
# ==========================
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]

    def perform_create(self, serializer):
        if self.request.user.is_school_admin:
            serializer.save(institution=self.request.user.institution)
        else:
            serializer.save()


# ==========================
# User Detail & Update Views
# ==========================
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameInstitution]
    lookup_field = 'pk'


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrSameInstitution]
    lookup_field = 'pk'


# ==========================
# Institution Views
# ==========================
class InstitutionCreateView(generics.CreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]


class InstitutionDetailView(generics.RetrieveAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    lookup_field = 'pk'
