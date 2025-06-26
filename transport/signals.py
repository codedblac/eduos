# transport/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import (
    TransportBooking,
    MaintenanceRecord,
    Vehicle,
    TripLog
)
from notifications.utils import send_notification
from django.utils import timezone
from datetime import timedelta

@receiver(post_save, sender=TransportBooking)
def handle_booking_creation(sender, instance, created, **kwargs):
    if created:
        # Notify driver or transport admin
        message = f"New transport booking requested by {instance.requested_by.get_full_name()} for {instance.purpose}"
        send_notification(
            institution=instance.institution,
            title="New Transport Booking",
            message=message,
            roles=["transport_admin", "driver"]
        )
    elif instance.status == "approved" and not instance.notified:
        # Send confirmation to requester
        message = f"Your transport booking from {instance.start_time} to {instance.end_time} has been approved."
        send_notification(
            institution=instance.institution,
            title="Booking Approved",
            message=message,
            users=[instance.requested_by]
        )
        instance.notified = True
        instance.save(update_fields=['notified'])

@receiver(post_save, sender=MaintenanceRecord)
def notify_maintenance_logged(sender, instance, created, **kwargs):
    if created:
        message = f"A new maintenance record has been added for vehicle {instance.vehicle.name}: {instance.issue_reported}"
        send_notification(
            institution=instance.institution,
            title="Vehicle Maintenance Recorded",
            message=message,
            roles=["transport_admin", "mechanic"]
        )

@receiver(post_save, sender=TripLog)
def track_trip_completion(sender, instance, created, **kwargs):
    if created and instance.end_time:
        duration = (instance.end_time - instance.start_time).total_seconds() / 3600
        message = f"Trip by {instance.driver.get_full_name()} from {instance.start_time} to {instance.end_time} completed. Duration: {duration:.2f} hrs"
        send_notification(
            institution=instance.institution,
            title="Trip Completed",
            message=message,
            roles=["transport_admin"]
        )

@receiver(pre_save, sender=Vehicle)
def alert_low_fuel_or_maintenance_due(sender, instance, **kwargs):
    try:
        old = Vehicle.objects.get(pk=instance.pk)
        if instance.fuel_level < 15 and old.fuel_level >= 15:
            send_notification(
                institution=instance.institution,
                title="Low Fuel Alert",
                message=f"{instance.name} has low fuel ({instance.fuel_level}%)",
                roles=["transport_admin"]
            )
        if instance.last_maintenance and instance.last_maintenance + timedelta(days=180) < timezone.now():
            send_notification(
                institution=instance.institution,
                title="Maintenance Due",
                message=f"{instance.name} may be due for maintenance (last: {instance.last_maintenance})",
                roles=["transport_admin"]
            )
    except Vehicle.DoesNotExist:
        pass
