from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    Role, Permission, RolePermission, UserRoleAssignment,
    RoleAuditLog, PermissionAuditLog
)
from .serializers import (
    RoleSerializer, PermissionSerializer, RolePermissionSerializer,
    UserRoleAssignmentSerializer, UserRoleAssignmentDetailSerializer,
    RoleAuditLogSerializer
)
from .filters import (
    RoleFilter, PermissionFilter, RolePermissionFilter,
    UserRoleAssignmentFilter, RoleAuditLogFilter, PermissionAuditLogFilter
)
from .permissions import HasInstitutionPermission, IsInstitutionMember


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RoleFilter
    search_fields = [ 'description']
    ordering_fields = [ 'created_at']
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        primary_role= self.get_object()
        perms = role.permissions.all()
        serializer = PermissionSerializer(perms, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PermissionFilter
    search_fields = ['codename', 'module']
    ordering_fields = ['codename', 'module']
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RolePermissionFilter
    search_fields = ['role__name', 'permission__codename']
    ordering_fields = ['primary_role', 'permission']
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]


class UserRoleAssignmentViewSet(viewsets.ModelViewSet):
    queryset = UserRoleAssignment.objects.all().select_related('user', 'primary_role', 'institution')
    serializer_class = UserRoleAssignmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserRoleAssignmentFilter
    search_fields = ['user__username', 'role__name', 'institution__name']
    ordering_fields = ['assigned_at', 'expires_at']
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return UserRoleAssignmentDetailSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        assignment = self.get_object()
        assignment.is_active = True
        assignment.save()
        return Response({'status': 'Role assignment activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        assignment = self.get_object()
        assignment.is_active = False
        assignment.save()
        return Response({'status': 'Role assignment deactivated'})


class RoleAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RoleAuditLog.objects.all().select_related('actor', 'primary_role', 'target_user', 'institution')
    serializer_class = RoleAuditLogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RoleAuditLogFilter
    search_fields = ['actor__username', 'target_user__username', 'role__name']
    ordering_fields = ['timestamp']
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]


class PermissionAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PermissionAuditLog.objects.all().select_related('actor', 'permission', 'target_role')
    serializer_class = RoleAuditLogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PermissionAuditLogFilter
    search_fields = ['actor__username', 'permission__codename', 'target_role__name']
    ordering_fields = ['timestamp']
    permission_classes = [permissions.IsAuthenticated, IsInstitutionMember]
