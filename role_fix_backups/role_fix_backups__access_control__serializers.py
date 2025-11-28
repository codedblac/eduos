from rest_framework import serializers
from .models import (
    Role, Permission, RolePermission, UserRoleAssignment,
    RoleAuditLog, PermissionAuditLog, UserPermissionOverride, PermissionUsageLog
)
from institutions.models import Institution
from django.contrib.auth import get_user_model

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class RolePermissionSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.PrimaryKeyRelatedField(
        source='permission', queryset=Permission.objects.all(), write_only=True
    )

    class Meta:
        model = RolePermission
        fields = ['role', 'permission', 'permission_id', 'allow']


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_permissions(self, obj):
        perms = RolePermission.objects.filter(primary_role=obj)
        return RolePermissionSerializer(perms, many=True).data


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_permissions(self, obj):
        perms = RolePermission.objects.filter(primary_role=obj)
        return RolePermissionSerializer(perms, many=True).data


class UserRoleAssignmentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    primary_role= serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all())

    class Meta:
        model = UserRoleAssignment
        fields = '__all__'


class UserRoleAssignmentDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    primary_role= RoleDetailSerializer(read_only=True)
    institution = serializers.StringRelatedField()

    class Meta:
        model = UserRoleAssignment
        fields = '__all__'


class UserPermissionOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermissionOverride
        fields = '__all__'


class RoleAuditLogSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField()
    target_user = serializers.StringRelatedField()
    primary_role= serializers.StringRelatedField()
    institution = serializers.StringRelatedField()

    class Meta:
        model = RoleAuditLog
        fields = '__all__'


class PermissionAuditLogSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField()
    permission = serializers.StringRelatedField()
    target_role = serializers.StringRelatedField()

    class Meta:
        model = PermissionAuditLog
        fields = '__all__'


class PermissionUsageLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    permission = serializers.StringRelatedField()

    class Meta:
        model = PermissionUsageLog
        fields = '__all__'
