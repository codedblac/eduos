# staff/tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import StaffLeave, StaffProfile, EmploymentHistory
from notifications.utils import send_notification_to_user


@shared_task
def send_leave_reminder_emails():
    """
    Notify HR and concerned staff members about pending leave requests.
    """
    pending_leaves = StaffLeave.objects.filter(status=StaffLeave.PENDING)
    for leave in pending_leaves:
        message = f"Leave request for {leave.staff_profile.user.get_full_name()} from {leave.start_date} to {leave.end_date} is still pending."
        send_notification_to_user(leave.staff_profile.user, title="Pending Leave Request", message=message)
        if leave.staff_profile.line_manager:
            send_notification_to_user(leave.staff_profile.line_manager, title="Approval Pending", message=message)


@shared_task
def check_contract_expiry():
    """
    Checks if any staff member's contract is nearing expiry and notifies HR.
    """
    upcoming_expiry = timezone.now().date() + timedelta(days=30)
    staff_members = StaffProfile.objects.filter(contract_end__lte=upcoming_expiry, is_active=True)

    for staff in staff_members:
        msg = f"Contract for {staff.user.get_full_name()} is ending on {staff.contract_end}. Please review for renewal or termination."
        # Notify HR Managers only
        from accounts.models import CustomUser
        hr_users = CustomUser.objects.filter(groups__name='HR Manager')
        for hr in hr_users:
            send_notification_to_user(hr, title="Contract Expiry Notice", message=msg)


@shared_task
def log_employment_anniversaries():
    """
    Sends congratulatory messages to staff on their employment anniversaries.
    """
    today = timezone.now().date()
    anniversary_staff = StaffProfile.objects.filter(date_joined__month=today.month, date_joined__day=today.day)

    for staff in anniversary_staff:
        years = today.year - staff.date_joined.year
        message = f"Congratulations on your {years} year(s) work anniversary at EduOS!"
        send_notification_to_user(staff.user, title="Work Anniversary", message=message)


@shared_task
def clean_expired_leaves():
    """
    Auto-close expired unapproved leave requests.
    """
    today = timezone.now().date()
    expired_leaves = StaffLeave.objects.filter(status=StaffLeave.PENDING, end_date__lt=today)
    for leave in expired_leaves:
        leave.status = StaffLeave.REJECTED
        leave.notes = "Auto-closed due to inactivity."
        leave.save()
