from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
import uuid

User = settings.AUTH_USER_MODEL

class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='roles', null=True, blank=True)
    is_system_role = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='child_roles')
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'institution')

    def __str__(self):
        return f"{self.name} ({'Global' if not self.institution else self.institution.name})"


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codename = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    module = models.CharField(max_length=100, help_text="e.g., finance, academics, chat")
    scope = models.CharField(max_length=50, default='institution')  # global, institution, module, object
    rules = models.JSONField(default=dict, blank=True)
    is_global = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codename}"


class RolePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    primary_role= models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    allow = models.BooleanField(default=True)

    class Meta:
        unique_together = ('primary_role', 'permission')

    def __str__(self):
        return f"{self.primary_role.name} - {self.permission.codename} ({'Allow' if self.allow else 'Deny'})"


class UserRoleAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    primary_role= models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_assignments')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='user_roles')
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'primary_role', 'institution')

    def __str__(self):
        return f"{self.user} - {self.primary_role.name} ({self.institution})"


class UserPermissionOverride(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_overrides')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    allow = models.BooleanField(default=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'permission', 'institution')

    def __str__(self):
        return f"{self.user} - {self.permission.codename} ({'Allow' if self.allow else 'Deny'})"


class RoleAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ACTIONS = [
        ('assign', 'Assigned'),
        ('remove', 'Removed'),
        ('update', 'Updated'),
        ('create', 'Created'),
        ('deactivate', 'Deactivated'),
    ]

    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_audit_logs')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='affected_roles')
    primary_role= models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.actor} {self.get_action_display()} {self.primary_role} for {self.target_user}"


class PermissionAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='permission_audit_logs')
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True)
    target_role = models.ForeignKey(Role, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=[('add', 'Added'), ('remove', 'Removed')])
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.actor} {self.get_action_display()} {self.permission} on {self.target_role}"


class PermissionUsageLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    context = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user} used {self.permission.codename} on {self.timestamp}"
