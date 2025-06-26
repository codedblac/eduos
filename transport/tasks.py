from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count
from celery import shared_task
from .models import (
    TransportAttendance, StudentTransportAssignment,
    Vehicle, TransportRoute, Driver
)
from notifications.utils import send_notification_to_user
from django.conf import settings

@shared_task
def mark_absent_students():
    """
    Automatically mark absent students who were assigned today but no check-in recorded.
    """
    today = timezone.now().date()
    assignments = StudentTransportAssignment.objects.filter(is_active=True)

    for assignment in assignments:
        if not TransportAttendance.objects.filter(
            date=today,
            student=assignment.student,
            route=assignment.route,
            vehicle=assignment.vehicle
        ).exists():
            TransportAttendance.objects.create(
                student=assignment.student,
                vehicle=assignment.vehicle,
                route=assignment.route,
                date=today,
                status='absent',
                institution=assignment.institution
            )


@shared_task
def send_morning_reminders():
    """
    Send daily transport reminders to parents and students in the morning.
    """
    now = timezone.now()
    assignments = StudentTransportAssignment.objects.filter(is_active=True)

    for assignment in assignments:
        student = assignment.student
        guardian_links = student.guardianstudentlink_set.all()

        for link in guardian_links:
            guardian = link.guardian.user
            send_notification_to_user(
                user=guardian,
                title="Transport Reminder",
                message=f"{student.full_name()} is assigned to route {assignment.route.name} today. Please ensure they are ready by {assignment.pickup_time.strftime('%I:%M %p') if assignment.pickup_time else 'assigned time'}."
            )


@shared_task
def suggest_route_balancing():
    """
    AI-assisted load balancer: flag routes that are overloaded and suggest alternatives.
    """
    overloaded_routes = (
        StudentTransportAssignment.objects.values('route')
        .annotate(student_count=Count('student'))
        .filter(student_count__gt=settings.MAX_ROUTE_CAPACITY)
    )

    for entry in overloaded_routes:
        route_id = entry['route']
        try:
            route = TransportRoute.objects.get(id=route_id)
            # In real deployment: notify admin or generate a dashboard alert
            print(f"[ALERT] Route '{route.name}' has exceeded capacity ({entry['student_count']} students). Consider re-assigning.")
        except TransportRoute.DoesNotExist:
            continue


@shared_task
def notify_driver_daily_schedule():
    """
    Send personalized daily route summaries to each driver every morning.
    """
    today = timezone.now().date()
    drivers = Driver.objects.all()

    for driver in drivers:
        assignments = StudentTransportAssignment.objects.filter(
            vehicle=driver.vehicle,
            is_active=True
        ).select_related('route', 'student')

        route_names = set([a.route.name for a in assignments])
        students = [a.student.full_name() for a in assignments]

        if assignments.exists():
            send_notification_to_user(
                user=driver.user,
                title="Today's Transport Schedule",
                message=f"You have {len(students)} students to transport across {', '.join(route_names)} today."
            )
