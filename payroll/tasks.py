# payroll/tasks.py

import datetime
from django.utils import timezone
from django.db.models import Sum
from celery import shared_task

from .models import (
    PayrollRun, Payslip, PayrollProfile, Allowance, Deduction,
    SalaryAdvanceRequest, PayrollAuditLog
)
from notifications.utils import send_notification_to_user
from .ai import PayrollAIEngine


@shared_task
def generate_monthly_payslips(payroll_run_id):
    try:
        payroll_run = PayrollRun.objects.get(id=payroll_run_id)
        payroll_profiles = PayrollProfile.objects.select_related('staff_profile__user').filter(is_active=True)

        for profile in payroll_profiles:
            staff = profile.staff_profile
            user = staff.user

            total_allowances = Allowance.objects.filter(staff_profile=staff).aggregate(total=Sum('amount'))['total'] or 0
            total_deductions = Deduction.objects.filter(staff_profile=staff).aggregate(total=Sum('amount'))['total'] or 0

            gross_salary = profile.basic_salary + total_allowances
            net_pay = gross_salary - total_deductions

            Payslip.objects.create(
                payroll_run=payroll_run,
                staff_profile=staff,
                gross_salary=gross_salary,
                total_allowances=total_allowances,
                total_deductions=total_deductions,
                net_pay=net_pay
            )

            # Notify the staff member
            send_notification_to_user(
                user=user,
                title="Payslip Generated",
                message=f"Your payslip for period {payroll_run.period_start.strftime('%b %Y')} has been generated.",
                notification_type="payslip"
            )

        payroll_run.is_locked = True
        payroll_run.processed_on = timezone.now()
        payroll_run.save()

    except Exception as e:
        PayrollAuditLog.objects.create(
            action="Payslip Generation Failed",
            performed_by=None,
            changes={"error": str(e)},
            staff_profile=None
        )


@shared_task
def run_payroll_anomaly_checks(payroll_run_id):
    """
    Run anomaly detection on recently processed payroll data.
    """
    payroll_run = PayrollRun.objects.get(id=payroll_run_id)
    anomalies = PayrollAIEngine(payroll_run)

    for anomaly in anomalies:
        send_notification_to_user(
            user=anomaly['user'],
            title="Payroll Anomaly Detected",
            message=anomaly['message'],
            notification_type="alert"
        )


@shared_task
def detect_fraud_patterns():
    """
    Global fraud pattern detection — across recent payroll activity.
    """
    issues = PayrollAIEngine()

    for issue in issues:
        send_notification_to_user(
            user=issue['user'],
            title="⚠️ Payroll Fraud Alert",
            message=issue['message'],
            notification_type="critical"
        )


@shared_task
def auto_approve_salary_advances():
    """
    Automatically approve small advances (<= KES 3,000).
    Notify finance for higher amounts.
    """
    pending_requests = SalaryAdvanceRequest.objects.filter(status='pending')

    for request in pending_requests:
        staff_user = request.staff_profile.user
        if request.amount <= 3000:
            request.status = 'approved'
            request.reviewed_on = timezone.now()
            request.save()
            send_notification_to_user(
                user=staff_user,
                title="Salary Advance Approved",
                message=f"Your salary advance of KES {request.amount} has been automatically approved.",
                notification_type="finance"
            )
        else:
            send_notification_to_user(
                user=staff_user,
                title="Salary Advance Pending",
                message="Your salary advance is pending finance review due to high requested amount.",
                notification_type="finance"
            )
