from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    VisitorLog, Appointment, ParcelDelivery, GatePass,
    FrontDeskTicket, FrontAnnouncement, SecurityLog
)


class FrontOfficeAnalyticsEngine:
    def __init__(self, institution):
        self.institution = institution
        self.now = timezone.now()
        self.today = self.now.date()

    # ---------------------- Visitors ----------------------
    def visitor_summary(self):
        queryset = VisitorLog.objects.filter(institution=self.institution)

        return {
            "total_today": queryset.filter(visit_date=self.today).count(),
            "this_week": queryset.filter(visit_date__gte=self.today - timedelta(days=7)).count(),
            "top_purposes": queryset.values("visit_purpose").annotate(count=Count("id")).order_by("-count")[:5],
            "average_visit_duration": queryset.exclude(check_out_time=None).annotate(
                duration=Count("check_out_time") - Count("check_in_time")
            ).aggregate(avg=Avg("duration"))["avg"]
        }

    # ---------------------- Appointments ----------------------
    def appointment_summary(self):
        queryset = Appointment.objects.filter(institution=self.institution)

        return {
            "scheduled_today": queryset.filter(meeting_date=self.today, status='scheduled').count(),
            "cancelled": queryset.filter(status='cancelled').count(),
            "top_staff_by_appointments": queryset.values("meeting_with__email").annotate(
                count=Count("id")
            ).order_by("-count")[:5]
        }

    # ---------------------- Parcel Deliveries ----------------------
    def parcel_summary(self):
        queryset = ParcelDelivery.objects.filter(institution=self.institution)

        return {
            "pending_pickup": queryset.filter(status='pending').count(),
            "overdue": queryset.filter(status='overdue').count(),
            "received_today": queryset.filter(received_on=self.today).count(),
        }

    # ---------------------- Gate Pass ----------------------
    def gate_pass_summary(self):
        queryset = GatePass.objects.filter(institution=self.institution)

        return {
            "total_today": queryset.filter(exit_time__date=self.today).count(),
            "pending": queryset.filter(status='pending').count(),
            "top_reasons": queryset.values("reason").annotate(count=Count("id")).order_by("-count")[:3],
        }

    # ---------------------- Front Desk Tickets ----------------------
    def ticket_summary(self):
        queryset = FrontDeskTicket.objects.filter(institution=self.institution)

        return {
            "open": queryset.filter(status='open').count(),
            "resolved": queryset.filter(status='resolved').count(),
            "average_resolution_time_hours": queryset.exclude(resolved_on=None).annotate(
                hours=(Count("resolved_on") - Count("created_on"))
            ).aggregate(avg=Avg("hours"))["avg"]
        }

    # ---------------------- Announcements ----------------------
    def announcement_summary(self):
        queryset = FrontAnnouncement.objects.filter(institution=self.institution)

        return {
            "active_count": queryset.count(),
            "recent_announcements": queryset.order_by("-created_on")[:5].values("message", "created_on")
        }

    # ---------------------- Security Logs ----------------------
    def security_log_summary(self):
        queryset = SecurityLog.objects.filter(institution=self.institution)

        return {
            "entries_today": queryset.filter(timestamp__date=self.today).count(),
            "entry_type_distribution": queryset.values("entry_type").annotate(count=Count("id")),
            "vehicle_entries": queryset.filter(~Q(vehicle_plate="")).count()
        }

    # ---------------------- Unified Dashboard ----------------------
    def get_full_dashboard(self):
        return {
            "visitors": self.visitor_summary(),
            "appointments": self.appointment_summary(),
            "parcels": self.parcel_summary(),
            "gate_passes": self.gate_pass_summary(),
            "tickets": self.ticket_summary(),
            "announcements": self.announcement_summary(),
            "security_logs": self.security_log_summary(),
        }
