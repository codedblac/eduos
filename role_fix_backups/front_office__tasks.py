from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from .models import (
    VisitorLog, ParcelDelivery, Appointment, FrontAnnouncement,
    FrontDeskTicket, SecurityLog, GatePass
)
from institutions.models import Institution
from .ai import FrontOfficeAIEngine
from notifications.utils import notify_admins  # Assumes this helper exists


@shared_task
def auto_checkout_visitors():
    threshold = timezone.now() - timedelta(hours=6)
    visitors = VisitorLog.objects.filter(check_out_time__isnull=True, visit_date__lte=threshold.date())

    for visitor in visitors:
        visitor.check_out_time = timezone.now()
        visitor.save()


@shared_task
def send_appointment_reminders():
    upcoming_appointments = Appointment.objects.filter(
        meeting_date=timezone.now().date(),
        meeting_time__gte=timezone.now().time(),
        status='scheduled'
    )

    for appointment in upcoming_appointments:
        if appointment.meeting_with.email:
            send_mail(
                subject="Upcoming Appointment Reminder",
                message=f"Hi {appointment.meeting_with.get_full_name()}, you have a meeting with {appointment.visitor_name} today at {appointment.meeting_time}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[appointment.meeting_with.email]
            )


@shared_task
def flag_undelivered_parcels():
    overdue_threshold = timezone.now() - timedelta(days=2)
    overdue_parcels = ParcelDelivery.objects.filter(status='pending', received_on__lte=overdue_threshold)

    for parcel in overdue_parcels:
        parcel.status = 'overdue'
        parcel.save()


@shared_task
def archive_old_announcements():
    cutoff = timezone.now() - timedelta(days=30)
    FrontAnnouncement.objects.filter(created_on__lte=cutoff).delete()


# ---------------- AI-Driven Additions ----------------


@shared_task
def analyze_security_logs():
    for institution in Institution.objects.all():
        message = FrontOfficeAIEngine.analyze_security_entries(institution)
        if "High volume" in message:
            notify_admins(
                institution=institution,
                title="🚨 Security Alert",
                message=message,
                source="front_office"
            )


@shared_task
def update_ticket_priorities():
    updates = FrontOfficeAIEngine.prioritize_tickets()
    for ticket_id, priority in updates.items():
        try:
            ticket = FrontDeskTicket.objects.get(id=ticket_id)
            ticket.priority = priority
            ticket.save(update_fields = ["priority"])
        except FrontDeskTicket.DoesNotExist:
            continue


@shared_task
def send_daily_visit_suggestions():
    for institution in Institution.objects.all():
        for user in institution.users.filter(primary_role='front_office'):
            suggestions = FrontOfficeAIEngine.suggest_visit_times(user)
            if suggestions:
                notify_admins(
                    institution=institution,
                    title="📈 Suggested Visitor Hours",
                    message=f"Least busy visitor times: {', '.join(str(h)+'h' for h in suggestions)}",
                    source="front_office"
                )


@shared_task
def gate_pass_risk_alerts():
    risky_ids = FrontOfficeAIEngine.predict_gate_pass_risk()
    if risky_ids:
        notify_admins(
            title="⚠️ Risky Gate Pass Requests",
            message=f"Gate passes flagged for review: IDs {risky_ids}",
            source="front_office"
        )


@shared_task
def delivery_insights():
    for institution in Institution.objects.all():
        trends = FrontOfficeAIEngine.delivery_trends(institution)
        if trends['peak_hours']:
            notify_admins(
                institution=institution,
                title="📦 Parcel Trends",
                message=f"Top delivery hours: {[h['hour'] for h in trends['peak_hours']]}, Top senders: {[s['sender_name'] for s in trends['top_senders']]}",
                source="front_office"
            )
