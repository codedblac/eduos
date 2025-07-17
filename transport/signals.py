from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import (
    TransportBooking,
    MaintenanceRecord,
    Vehicle,
    TripLog
)
from notifications.utils import send_notification


@receiver(post_save, sender=TransportBooking)
def handle_booking_creation(sender, instance, created, **kwargs):
    if created:
        message = f"New transport booking for {instance.student.full_name()} on {instance.travel_date}."
        send_notification(
            institution=instance.institution,
            title="New Transport Booking",
            message=message,
            roles=["transport_admin"]
        )

    elif instance.status == "confirmed":
        message = f"Your transport booking for {instance.travel_date} has been confirmed."
        send_notification(
            institution=instance.institution,
            title="Booking Confirmed",
            message=message,
            users=[instance.booked_by]
        )


@receiver(post_save, sender=MaintenanceRecord)
def notify_maintenance_logged(sender, instance, created, **kwargs):
    if created:
        message = f"New maintenance: {instance.maintenance_type} for {instance.vehicle.plate_number}."
        send_notification(
            institution=instance.institution,
            title="Maintenance Record Added",
            message=message,
            roles=["transport_admin", "mechanic"]
        )


@receiver(post_save, sender=TripLog)
def track_trip_completion(sender, instance, created, **kwargs):
    if instance.status == "completed" and instance.end_time:
        duration = (instance.end_time - instance.start_time).total_seconds() / 3600
        message = (
            f"Trip completed for route {instance.route.name} by {instance.driver.user.get_full_name()}.\n"
            f"Duration: {duration:.2f} hrs"
        )
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
        # Only alert if the fuel level dropped significantly
        if hasattr(instance, "fuel_level") and hasattr(old, "fuel_level"):
            if instance.fuel_level < 15 and old.fuel_level >= 15:
                send_notification(
                    institution=instance.institution,
                    title="Low Fuel Alert",
                    message=f"Vehicle {instance.plate_number} has low fuel ({instance.fuel_level}%)",
                    roles=["transport_admin"]
                )

        if instance.last_service_date and instance.last_service_date + timedelta(days=180) < timezone.now().date():
            send_notification(
                institution=instance.institution,
                title="Maintenance Due",
                message=f"Vehicle {instance.plate_number} is overdue for maintenance (last: {instance.last_service_date})",
                roles=["transport_admin"]
            )
    except Vehicle.DoesNotExist:
        pass
