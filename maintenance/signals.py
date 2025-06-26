# maintenance/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MaintenanceRequest, MaintenanceLog
from django.utils.timezone import now


@receiver(post_save, sender=MaintenanceRequest)
def auto_log_maintenance_request(sender, instance, created, **kwargs):
    """
    Automatically create a MaintenanceLog entry when a request is approved and completed.
    """
    if instance.status == 'completed' and not MaintenanceLog.objects.filter(request=instance).exists():
        MaintenanceLog.objects.create(
            request=instance,
            equipment=instance.equipment,
            technician=instance.assigned_to,
            notes="Auto-generated log after request marked as completed.",
            completed_at=now(),
            institution=instance.institution
        )


@receiver(post_save, sender=MaintenanceRequest)
def notify_on_status_change(sender, instance, **kwargs):
    """
    Placeholder: Trigger notifications on request status updates.
    Can be extended to send email, Firebase, or in-app messages.
    """
    # Example: integrate with notifications app
    pass
