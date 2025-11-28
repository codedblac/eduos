# payroll/filters.py

import django_filters
from .models import (
    PayrollProfile, PayrollRun, Payslip,
    Allowance, Deduction, SalaryAdvanceRequest
)


class PayrollProfileFilter(django_filters.FilterSet):
    department = django_filters.CharFilter(field_name="staff_profile__department__name", lookup_expr='icontains')
    designation = django_filters.CharFilter(field_name="staff_profile__designation", lookup_expr='icontains')
    employment_type = django_filters.CharFilter(field_name="staff_profile__employment_type", lookup_expr='iexact')
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = PayrollProfile
        fields = ['staff_profile', 'department', 'designation', 'employment_type', 'is_active']


class PayrollRunFilter(django_filters.FilterSet):
    month = django_filters.NumberFilter(field_name="period_start__month")
    year = django_filters.NumberFilter(field_name="period_start__year")

    class Meta:
        model = PayrollRun
        fields = ['month', 'year']


class PayslipFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff_profile__id")
    month = django_filters.NumberFilter(field_name="payroll_run__period_start__month")
    year = django_filters.NumberFilter(field_name="payroll_run__period_start__year")
    net_pay_min = django_filters.NumberFilter(field_name="net_pay", lookup_expr='gte')
    net_pay_max = django_filters.NumberFilter(field_name="net_pay", lookup_expr='lte')

    class Meta:
        model = Payslip
        fields = ['staff', 'month', 'year', 'net_pay_min', 'net_pay_max']


class AllowanceFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff_profile__id")
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='lte')

    class Meta:
        model = Allowance
        fields = ['staff', 'min_amount', 'max_amount']


class DeductionFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff_profile__id")
    type = django_filters.CharFilter(field_name="type", lookup_expr='icontains')
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='lte')

    class Meta:
        model = Deduction
        fields = ['staff', 'type', 'min_amount', 'max_amount']


class SalaryAdvanceRequestFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff_profile__id")
    status = django_filters.ChoiceFilter(choices=SalaryAdvanceRequest.STATUS_CHOICES)
    month = django_filters.NumberFilter(field_name="requested_on__month")
    year = django_filters.NumberFilter(field_name="requested_on__year")

    class Meta:
        model = SalaryAdvanceRequest
        fields = ['staff', 'status', 'month', 'year']
