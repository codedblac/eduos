from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    UserRoleAssignment,
    RolePermission,
    RoleAuditLog,
    PermissionAuditLog,
    # ApprovalRequest,
)
from .tasks import log_role_assignment_change, log_permission_change, sync_permissions_for_role

User = get_user_model()


@receiver(post_save, sender=UserRoleAssignment)
def handle_role_assignment_create_or_update(sender, instance, created, **kwargs):
    """
    Logs when a role is assigned or updated to a user.
    Triggers async audit log and permission sync.
    """
    action = "assign" if created else "update"
    actor_id = getattr(instance, 'assigned_by', None).id if hasattr(instance, 'assigned_by') and instance.assigned_by else None

    if actor_id:
        log_role_assignment_change.delay(
            actor_id=actor_id,
            user_id=instance.user.id,
            institution_id=instance.institution.id,
            role_id=instance.role.id,
            action=action,
            notes="Automatic role assignment log"
        )
    sync_permissions_for_role.delay(instance.role.id)


@receiver(pre_delete, sender=UserRoleAssignment)
def handle_role_assignment_deletion(sender, instance, **kwargs):
    """
    Logs when a role is removed from a user.
    """
    actor_id = getattr(instance, 'assigned_by', None).id if hasattr(instance, 'assigned_by') and instance.assigned_by else None
    if actor_id:
        log_role_assignment_change.delay(
            actor_id=actor_id,
            user_id=instance.user.id,
            institution_id=instance.institution.id,
            role_id=instance.role.id,
            action="remove",
            notes="Role removed"
        )


@receiver(post_save, sender=RolePermission)
def handle_role_permission_update(sender, instance, created, **kwargs):
    """
    Triggers permission audit log and role sync task.
    """
    actor = getattr(instance, '_actor', None)
    action = "add" if created else "update"
    if actor:
        log_permission_change.delay(
            actor_id=actor.id,
            permission_id=instance.permission.id,
            role_id=instance.role.id,
            action=action,
            notes="Permission assigned via API"
        )
    sync_permissions_for_role.delay(instance.role.id)


# @receiver(post_save, sender=ApprovalRequest)
# def handle_approval_request(sender, instance, created, **kwargs):
#     """
#     Logs actions related to approval workflows (approve/reject).
#     """
#     if not created and instance.status in ["approved", "rejected"]:
#         RoleAuditLog.objects.create(
#             actor=instance.approved_by,
#             target_user=instance.requested_by,
#             institution=instance.institution,
#             role=None,
#             action="update",
#             notes=f"{instance.status.title()} approval request: {instance.request_type} (Ref ID: {instance.reference_id})"
#         )
