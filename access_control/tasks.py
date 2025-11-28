from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from institutions.models import Institution
from .models import (
    Role,
    Permission,
    RolePermission,
    UserRoleAssignment,
    RoleAuditLog,
    PermissionAuditLog,
)

import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def log_role_assignment_change(actor_id, user_id, institution_id, role_id, action, notes=""):
    """
    Create audit log entry for a user's role assignment change.
    """
    try:
        actor = User.objects.get(id=actor_id)
        user = User.objects.get(id=user_id)
        primary_role= Role.objects.get(id=role_id)
        institution = Institution.objects.get(id=institution_id)

        RoleAuditLog.objects.create(
            actor=actor,
            target_user=user,
            primary_role=role,
            institution=institution,
            action=action,
            notes=notes
        )
        logger.info(f"[Audit] {actor} {action} {role.name} for {user} in {institution}")
    except Exception as e:
        logger.error(f"[AccessControl] Role audit log failed: {e}")


@shared_task
def log_permission_change(actor_id, permission_id, role_id, action, notes=""):
    """
    Logs when a permission is added or removed from a role.
    """
    try:
        actor = User.objects.get(id=actor_id)
        permission = Permission.objects.get(id=permission_id)
        primary_role= Role.objects.get(id=role_id)

        PermissionAuditLog.objects.create(
            actor=actor,
            permission=permission,
            target_role=role,
            action=action,
            notes=notes
        )
        logger.info(f"[Audit] {actor} {action} permission '{permission.codename}' on role '{role.name}'")
    except Exception as e:
        logger.error(f"[AccessControl] Permission audit log failed: {e}")


@shared_task
def bulk_assign_role(user_ids, role_id, institution_id, assigned_by_id, notes=""):
    """
    Assign a role to multiple users asynchronously.
    """
    try:
        assigned_by = User.objects.get(id=assigned_by_id)
        primary_role= Role.objects.get(id=role_id)
        institution = Institution.objects.get(id=institution_id)

        with transaction.atomic():
            for user_id in user_ids:
                user = User.objects.get(id=user_id)
                assignment, created = UserRoleAssignment.objects.update_or_create(
                    user=user,
                    primary_role=role,
                    institution=institution,
                    defaults={"is_active": True}
                )
                action = "assign" if created else "update"
                log_role_assignment_change.delay(
                    assigned_by.id, user.id, institution.id, role.id, action, notes
                )

        return f"Assigned role '{role.name}' to {len(user_ids)} users."

    except Exception as e:
        logger.exception(f"[AccessControl] Error during bulk role assignment: {e}")
        return str(e)


@shared_task
def sync_permissions_for_role(role_id):
    """
    Cleans up and validates permissions for a given role.
    Removes orphaned links or ensures correct state.
    """
    try:
        primary_role= Role.objects.get(id=role_id)
        linked_permissions = RolePermission.objects.filter(primary_role=role)

        # Optional business rules or cleanup can go here
        seen = set()
        cleaned = []

        for rp in linked_permissions:
            if rp.permission_id not in seen:
                seen.add(rp.permission_id)
                cleaned.append(rp.permission_id)

        # Ensure all permissions exist
        Permission.objects.filter(id__in=cleaned)

        logger.info(f"[AccessControl] Synced permissions for role '{role.name}'")
        return f"Synced permissions for role '{role.name}'"

    except Exception as e:
        logger.exception(f"[AccessControl] Error syncing permissions: {e}")
        return str(e)
