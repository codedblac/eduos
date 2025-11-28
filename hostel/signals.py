from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RoomAllocation, HostelLeaveRequest, HostelViolation, StockAlert
from notifications.utils import send_notification  # Assuming a shared notification system
from django.utils.timezone import now


@receiver(post_save, sender=RoomAllocation)
def notify_room_allocation(sender, instance, created, **kwargs):
    if created:
        message = f"Room {instance.room.name} allocated to {instance.student.user.get_full_name()}"
        send_notification(
            recipient=instance.student.user,
            title="Room Allocation",
            message=message,
            primary_role='student',
            institution=instance.institution
        )


@receiver(post_save, sender=HostelLeaveRequest)
def notify_leave_request(sender, instance, created, **kwargs):
    if created:
        send_notification(
            recipient=instance.student.user,
            title="Leave Request Submitted",
            message=f"Your leave request from {instance.leave_date} to {instance.return_date} has been submitted.",
            primary_role='student',
            institution=instance.institution
        )
    elif instance.approved:
        send_notification(
            recipient=instance.student.user,
            title="Leave Approved",
            message=f"Your leave request has been approved.",
            primary_role='student',
            institution=instance.institution
        )


@receiver(post_save, sender=HostelViolation)
def notify_violation_reported(sender, instance, created, **kwargs):
    if created:
        send_notification(
            recipient=instance.reported_by,
            title="Violation Report Logged",
            message=f"Violation in room {instance.room.name} reported.",
            primary_role='admin',
            institution=instance.institution
        )
