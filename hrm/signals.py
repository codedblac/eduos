from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    StaffHRRecord,
    HRDocument,
    PerformanceReview,
    LeaveRequest,
    DisciplinaryAction,
    HRAuditLog
)
from notifications.utils import send_notification_to_user


@receiver(post_save, sender=StaffHRRecord)
def log_staff_profile_created_or_updated(sender, instance, created, **kwargs):
    action = 'Created' if created else 'Updated'
    HRAuditLog.objects.create(
        staff=instance,
        action=action,
        performed_by=instance.user,
        details={
            'name': instance.user.get_full_name(),
            'branch': instance.branch.name if instance.branch else None,
            'department': instance.department.name if instance.department else None
        }
    )


@receiver(post_save, sender=HRDocument)
def notify_document_upload(sender, instance, created, **kwargs):
    if created and instance.staff and instance.staff.user:
        send_notification_to_user(
            user=instance.staff.user,
            title="Document Uploaded",
            message=f"Your HR document '{instance.title}' was uploaded successfully.",
            notification_type="document"
        )


@receiver(post_save, sender=LeaveRequest)
def notify_leave_status_change(sender, instance, **kwargs):
    if instance.status in ['approved', 'rejected'] and instance.staff and instance.staff.user:
        send_notification_to_user(
            user=instance.staff.user,
            title="Leave Request Update",
            message=f"Your leave request from {instance.start_date} to {instance.end_date} has been {instance.status.upper()}.",
            notification_type="leave"
        )


@receiver(post_save, sender=PerformanceReview)
def notify_performance_review_status(sender, instance, created, **kwargs):
    if created and instance.reviewer:
        send_notification_to_user(
            user=instance.reviewer,
            title="Performance Review Assigned",
            message=f"You've been assigned a performance review for {instance.staff.user.get_full_name()}.",
            notification_type="performance"
        )


@receiver(post_save, sender=DisciplinaryAction)
def notify_disciplinary_action_logged(sender, instance, created, **kwargs):
    if created and instance.staff and instance.staff.user:
        send_notification_to_user(
            user=instance.staff.user,
            title="New Disciplinary Action Logged",
            message=f"A disciplinary action has been recorded in your HR profile.",
            notification_type="discipline"
        )
