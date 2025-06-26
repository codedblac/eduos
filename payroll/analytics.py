# payroll/analytics.py

from django.db.models import Sum, Avg, Count
from .models import Payslip, PayrollProfile, PayrollRun, Allowance, Deduction
from staff.models import StaffProfile
from datetime import datetime


class PayrollAnalyticsEngine:
    def __init__(self, institution):
        self.institution = institution

    def total_payroll_cost(self, month=None, year=None):
        qs = Payslip.objects.filter(staff_profile__institution=self.institution)
        if month and year:
            qs = qs.filter(
                payroll_run__period_start__month=month,
                payroll_run__period_start__year=year
            )
        return qs.aggregate(total=Sum('net_pay'))['total'] or 0

    def average_salary_by_designation(self):
        return PayrollProfile.objects.filter(staff_profile__institution=self.institution)\
            .values('staff_profile__designation')\
            .annotate(avg_salary=Avg('basic_salary'))\
            .order_by('-avg_salary')

    def department_salary_distribution(self):
        return PayrollProfile.objects.filter(staff_profile__institution=self.institution)\
            .values('staff_profile__department__name')\
            .annotate(total=Sum('basic_salary'))\
            .order_by('-total')

    def most_common_deductions(self, top_n=5):
        return Deduction.objects.filter(staff_profile__institution=self.institution)\
            .values('type')\
            .annotate(total=Sum('amount'), count=Count('id'))\
            .order_by('-total')[:top_n]

    def most_common_allowances(self, top_n=5):
        return Allowance.objects.filter(staff_profile__institution=self.institution)\
            .values('name')\
            .annotate(total=Sum('amount'), count=Count('id'))\
            .order_by('-total')[:top_n]

    def monthly_payroll_trend(self, year=None):
        year = year or datetime.now().year
        return Payslip.objects.filter(
            staff_profile__institution=self.institution,
            payroll_run__period_start__year=year
        ).values('payroll_run__period_start__month')\
        .annotate(total=Sum('net_pay'))\
        .order_by('payroll_run__period_start__month')

    def staff_with_highest_deductions(self, limit=10):
        return Deduction.objects.filter(staff_profile__institution=self.institution)\
            .values(
                'staff_profile__id',
                'staff_profile__user__first_name',
                'staff_profile__user__last_name'
            )\
            .annotate(total=Sum('amount'))\
            .order_by('-total')[:limit]

    def staff_with_highest_allowances(self, limit=10):
        return Allowance.objects.filter(staff_profile__institution=self.institution)\
            .values(
                'staff_profile__id',
                'staff_profile__user__first_name',
                'staff_profile__user__last_name'
            )\
            .annotate(total=Sum('amount'))\
            .order_by('-total')[:limit]

    def current_payroll_summary(self):
        today = datetime.today()
        return {
            "total_net_pay": self.total_payroll_cost(month=today.month, year=today.year),
            "top_deductions": self.most_common_deductions(),
            "top_allowances": self.most_common_allowances(),
            "salary_distribution": self.department_salary_distribution(),
            "average_by_designation": self.average_salary_by_designation(),
        }
