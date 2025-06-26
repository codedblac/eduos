# payroll/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import (
    PayrollProfile,
    SalaryAdvanceRequest,
    Payslip,
    PayrollAuditLog
)
from notifications.utils import send_notification_to_user


@receiver(post_save, sender=PayrollProfile)
def log_payroll_profile_update(sender, instance, created, **kwargs):
    action = 'Created' if created else 'Updated'
    PayrollAuditLog.objects.create(
        staff_profile=instance.staff_profile,
        action=f"PayrollProfile {action}",
        changes={"basic_salary": str(instance.basic_salary), "tax_identifier": instance.tax_identifier},
        performed_by=None  # Optional: replace with audit middleware logic
    )


@receiver(post_save, sender=SalaryAdvanceRequest)
def notify_salary_advance_status(sender, instance, **kwargs):
    if instance.status in ['approved', 'rejected']:
        send_notification_to_user(
            user=instance.staff_profile.user,
            title="Salary Advance Status Update",
            message=f"Your salary advance request of KES {instance.amount} has been {instance.status.upper()}.",
            notification_type="finance"
        )


@receiver(pre_save, sender=Payslip)
def update_payslip_status(sender, instance, **kwargs):
    if not instance.pk:
        # Only on creation
        instance.generated_on = now()


@receiver(post_save, sender=Payslip)
def notify_payslip_generation(sender, instance, created, **kwargs):
    if created:
        run_period = instance.payroll_run.period_start.strftime('%B %Y')
        send_notification_to_user(
            user=instance.staff_profile.user,
            title="Payslip Available",
            message=f"Your payslip for {run_period} is now available in your portal.",
            notification_type="payslip"
        )


@receiver(post_save, sender=Payslip)
def log_payslip_event(sender, instance, created, **kwargs):
    PayrollAuditLog.objects.create(
        staff_profile=instance.staff_profile,
        action="Payslip Created" if created else "Payslip Updated",
        changes={
            "gross_salary": str(instance.gross_salary),
            "net_pay": str(instance.net_pay),
            "total_allowances": str(instance.total_allowances),
            "total_deductions": str(instance.total_deductions),
        },
        performed_by=None  # Replace with actual user from context if available
    )
