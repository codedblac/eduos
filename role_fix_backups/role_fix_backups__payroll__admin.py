from django.contrib import admin
from .models import (
    PayrollProfile, Allowance, Deduction, BankAccount,
    SalaryAdvanceRequest, PayrollRun, Payslip, PayrollAuditLog
)


@admin.register(PayrollProfile)
class PayrollProfileAdmin(admin.ModelAdmin):
    list_display = ['staff_profile', 'basic_salary', 'total_allowances_display', 'total_deductions_display', 'net_salary_display', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['staff_profile__user__first_name', 'staff_profile__user__last_name']

    def total_allowances_display(self, obj):
        return obj.total_allowances()
    total_allowances_display.short_description = "Total Allowances"

    def total_deductions_display(self, obj):
        return obj.total_deductions()
    total_deductions_display.short_description = "Total Deductions"

    def net_salary_display(self, obj):
        return obj.net_salary()
    net_salary_display.short_description = "Net Salary"


@admin.register(Allowance)
class AllowanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'staff_profile', 'is_taxable', 'created_at']
    list_filter = ['is_taxable']
    search_fields = ['name', 'staff_profile__user__first_name', 'staff_profile__user__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Deduction)
class DeductionAdmin(admin.ModelAdmin):
    list_display = ['type', 'amount', 'staff_profile', 'created_by', 'created_at']
    list_filter = ['type']
    search_fields = ['type', 'staff_profile__user__first_name', 'staff_profile__user__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['staff_profile', 'bank_name', 'account_name', 'account_number', 'is_primary']
    list_filter = ['bank_name', 'is_primary']
    search_fields = ['account_name', 'account_number', 'staff_profile__user__first_name', 'staff_profile__user__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SalaryAdvanceRequest)
class SalaryAdvanceRequestAdmin(admin.ModelAdmin):
    list_display = ['staff_profile', 'amount', 'status', 'requested_on', 'reviewed_by', 'reviewed_on']
    list_filter = ['status']
    search_fields = ['staff_profile__user__first_name', 'staff_profile__user__last_name']
    readonly_fields = ['requested_on', 'reviewed_on']


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ['institution', 'period_start', 'period_end', 'processed_on', 'processed_by', 'is_locked']
    list_filter = ['is_locked', 'period_start', 'period_end']
    search_fields = ['institution__name']
    readonly_fields = ['processed_on', 'created_at', 'updated_at']


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['staff_profile', 'payroll_run', 'gross_salary', 'total_allowances', 'total_deductions', 'net_pay', 'is_sent', 'generated_on']
    list_filter = ['is_sent', 'generated_on']
    search_fields = ['staff_profile__user__first_name', 'staff_profile__user__last_name']
    readonly_fields = ['generated_on']


@admin.register(PayrollAuditLog)
class PayrollAuditLogAdmin(admin.ModelAdmin):
    list_display = ['staff_profile', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['staff_profile__user__username', 'performed_by__username']
    readonly_fields = ['timestamp']
