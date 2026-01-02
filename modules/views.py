from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import SystemModule, SchoolModule, Plan
from .serializers import (
    SystemModuleSerializer,
    SchoolModuleSerializer,
    UserModuleAccessSerializer,
    AssignModulesSerializer,
    PlanSerializer
)

User = get_user_model()


# -----------------------------------------------
# 1. List all System Modules (Super Admin Only)
# -----------------------------------------------
class SystemModuleListView(generics.ListAPIView):
    serializer_class = SystemModuleSerializer
    queryset = SystemModule.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_super_admin:
            return SystemModule.objects.none()
        return super().get_queryset()


# -----------------------------------------------
# 2. List and Create Plans (Super Admin)
# -----------------------------------------------
class PlanListCreateView(generics.ListCreateAPIView):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_super_admin:
            return Plan.objects.none()
        return super().get_queryset()


# -----------------------------------------------
# 3. Assign Modules to School (Super Admin / Onboarding)
# -----------------------------------------------
class AssignModuleToSchoolView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_super_admin:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = AssignModulesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        school_modules = serializer.save()

        return Response(
            SchoolModuleSerializer(school_modules, many=True).data,
            status=status.HTTP_200_OK
        )


# -----------------------------------------------
# 4. Assign Modules to User (Institution Admin)
# -----------------------------------------------
class AssignModulesToUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_institution_admin:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        target_user_id = request.data.get("user_id")
        module_ids = request.data.get("module_ids", [])

        if not target_user_id or not module_ids:
            return Response(
                {"detail": "user_id and module_ids are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get target user within same institution
        target_user = User.objects.filter(id=target_user_id, institution=user.institution).first()
        if not target_user:
            return Response(
                {"detail": "User not found or not in your institution"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only assign modules that are allowed for the institution
        allowed_module_ids = list(target_user.institution.allowed_modules.values_list("module_id", flat=True))
        valid_module_ids = set(module_ids).intersection(allowed_module_ids)
        valid_modules = SystemModule.objects.filter(id__in=valid_module_ids)

        # Assign modules to user
        target_user.modules.set(valid_modules)
        target_user.save()

        return Response({
            "user": target_user.email,
            "assigned_modules": [m.name for m in valid_modules]
        }, status=status.HTTP_200_OK)


# -----------------------------------------------
# 5. Get Modules for Current User (Dynamic Sidebar)
# -----------------------------------------------
class CurrentUserModulesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserModuleAccessSerializer({"user_id": request.user.id})
        return Response(serializer.data)
