from django.contrib import admin
from .models import (
    Role, Permission, RolePermission,
    UserRoleAssignment, UserPermissionOverride,
    RoleAuditLog, PermissionAuditLog, PermissionUsageLog
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'is_system_role', 'is_active', 'created_at']
    list_filter = ['is_system_role', 'is_active', 'institution']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['codename', 'module', 'scope', 'is_global', 'created_at']
    list_filter = ['module', 'scope', 'is_global']
    search_fields = ['codename', 'description']
    ordering = ['codename']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'allow']
    list_filter = ['allow', 'role', 'permission']
    search_fields = ['role__name', 'permission__codename']
    ordering = ['role__name', 'permission__codename']


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'institution', 'is_active', 'assigned_at', 'expires_at']
    list_filter = ['is_active', 'institution', 'role']
    search_fields = ['user__username', 'role__name']
    ordering = ['-assigned_at']


@admin.register(UserPermissionOverride)
class UserPermissionOverrideAdmin(admin.ModelAdmin):
    list_display = ['user', 'permission', 'institution', 'allow', 'applied_at']
    list_filter = ['allow', 'institution', 'permission']
    search_fields = ['user__username', 'permission__codename']
    ordering = ['-applied_at']


@admin.register(RoleAuditLog)
class RoleAuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'target_user', 'role', 'institution', 'action', 'timestamp']
    list_filter = ['action', 'institution']
    search_fields = ['actor__username', 'target_user__username', 'role__name']
    ordering = ['-timestamp']


@admin.register(PermissionAuditLog)
class PermissionAuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'permission', 'target_role', 'action', 'timestamp']
    list_filter = ['action', 'target_role']
    search_fields = ['actor__username', 'target_role__name', 'permission__codename']
    ordering = ['-timestamp']


@admin.register(PermissionUsageLog)
class PermissionUsageLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'permission', 'action', 'timestamp']
    list_filter = ['permission']
    search_fields = ['user__username', 'permission__codename', 'action']
    ordering = ['-timestamp']
