from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import HostelInspection, RoomAllocation
from notifications.utils import send_notification


@shared_task
def send_daily_hostel_reminders():
    today = now().date()
    inspections = HostelInspection.objects.filter(date=today)
    for inspection in inspections:
        send_notification(
            recipient=inspection.inspected_by,
            title="Today's Hostel Inspection",
            message=f"You have a scheduled hostel inspection today in room {inspection.room.name}.",
            primary_role='staff',
            institution=inspection.institution
        )


@shared_task
def alert_about_expiring_allocations():
    upcoming_expiry = now().date() + timedelta(days=3)
    allocations = RoomAllocation.objects.filter(allocated_until=upcoming_expiry)
    for alloc in allocations:
        send_notification(
            recipient=alloc.student.user,
            title="Room Allocation Expiry Notice",
            message=f"Your room allocation for {alloc.room.name} will expire in 3 days.",
            primary_role='student',
            institution=alloc.institution
        )
