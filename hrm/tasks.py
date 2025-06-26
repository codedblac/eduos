from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import (
    StaffHRRecord, HRDocument, PerformanceReview, LeaveRequest
)
from notifications.utils import send_notification_to_user
from .ai import HRMAIEngine


@shared_task
def check_missing_documents():
    """
    Notify HR about missing critical documents for staff.
    (Assumes AI engine detects document compliance issues)
    """
    engine = HRMAIEngine()
    missing_docs = engine.detect_missing_documents()

    for issue in missing_docs:
        staff = issue.get("staff")
        if staff and staff.user:
            send_notification_to_user(
                user=staff.user,
                title="Missing Document Alert",
                message=issue.get("message", "Missing HR document detected."),
                notification_type="document"
            )


@shared_task
def trigger_performance_review_reminders():
    """
    Send reminders for overdue or upcoming performance reviews.
    """
    today = timezone.now().date()

    reviews = PerformanceReview.objects.filter(
        next_review_date__lte=today
    )

    for review in reviews:
        reviewer = review.reviewer
        if reviewer:
            send_notification_to_user(
                user=reviewer,
                title="Performance Review Due",
                message=f"A review for {review.staff.user.get_full_name()} is due or overdue.",
                notification_type="performance"
            )


@shared_task
def analyze_performance_anomalies():
    """
    Use AI to flag abnormal performance trends across all institutions.
    """
    engine = HRMAIEngine()
    anomalies = engine.detect_low_performance()

    for issue in anomalies:
        supervisor = issue.get("supervisor")
        if supervisor:
            send_notification_to_user(
                user=supervisor,
                title="Performance Anomaly Alert",
                message=issue.get("message", "A performance anomaly was detected."),
                notification_type="alert"
            )


@shared_task
def auto_flag_unapproved_leaves():
    """
    Automatically flag leave requests that have been pending for more than 5 days.
    """
    threshold_days = 5
    today = timezone.now().date()

    pending_leaves = LeaveRequest.objects.filter(status='pending')
    for leave in pending_leaves:
        days_pending = (today - leave.requested_on.date()).days
        if days_pending > threshold_days and leave.staff and leave.staff.user:
            send_notification_to_user(
                user=leave.staff.user,
                title="Leave Request Still Pending",
                message=f"Your leave request from {leave.requested_on.date()} is still pending.",
                notification_type="leave"
            )

