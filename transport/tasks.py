import datetime
from django.utils import timezone
from django.db.models import Q
from celery import shared_task
from .models import (
    MaintenanceRecord, Vehicle, TripLog, TransportNotification,
    TransportBooking, TransportAttendance, TransportRoute
)
from accounts.utils import notify_user  # Replace with your actual notification method


@shared_task
def send_daily_transport_notifications():
    """
    Notify guardians about today's pickup/drop status or delays.
    """
    today = timezone.now().date()
    unsent_notifications = TransportNotification.objects.filter(is_sent=False, sent_at__date=today)
    for notif in unsent_notifications:
        if notif.recipient_guardian:
            notify_user(
                user=notif.recipient_guardian,
                message=notif.message,
                title=f"Transport Alert: {notif.get_type_display()}",
                data={"student_id": notif.student_id, "type": notif.type}
            )
            notif.is_sent = True
            notif.save()


@shared_task
def flag_vehicles_due_for_maintenance():
    """
    Check if any vehicle is due for maintenance based on last service + schedule.
    """
    today = timezone.now().date()
    upcoming_due = MaintenanceRecord.objects.filter(
        next_due_date__lte=today,
        vehicle__isnull=False
    ).select_related("vehicle")
    for record in upcoming_due:
        message = f"Vehicle {record.vehicle.plate_number} is due for maintenance: {record.maintenance_type}"
        notify_user(
            user=None,  # Send to transport admin group
            message=message,
            title="Maintenance Alert",
            data={"vehicle_id": record.vehicle.id}
        )


@shared_task
def archive_old_trip_logs():
    """
    Auto-archive trip logs older than 90 days.
    """
    cutoff = timezone.now() - datetime.timedelta(days=90)
    TripLog.objects.filter(end_time__lt=cutoff, status="completed").update(status="archived")


@shared_task
def auto_cancel_unconfirmed_bookings():
    """
    Cancel all transport bookings for today that are still in 'pending' status after 6 AM.
    """
    now = timezone.now()
    today = now.date()
    cutoff_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
    if now > cutoff_time:
        TransportBooking.objects.filter(
            travel_date=today,
            status="pending"
        ).update(status="cancelled")


@shared_task
def record_daily_transport_attendance():
    """
    Auto-fill 'absent' attendance for students with transport assignments but no attendance record.
    """
    today = timezone.now().date()
    from students.models import Student  # Lazy import to avoid circular import

    assigned_students = Student.objects.filter(
        transportassignment__is_active=True
    ).distinct()

    for student in assigned_students:
        if not student.transportattendance_set.filter(date=today).exists():
            from accounts.models import CustomUser
            system_user = CustomUser.objects.filter(username="system").first()
            student.transportattendance_set.create(
                date=today,
                status="absent",
                recorded_by=system_user,
                institution=student.institution
            )
