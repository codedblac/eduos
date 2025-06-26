from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PayrollProfileViewSet, AllowanceViewSet, DeductionViewSet,
    PayrollRunViewSet, PayslipViewSet, PayrollAuditLogViewSet,
    SalaryAdvanceRequestViewSet, BankAccountViewSet,
    PayrollAnalyticsView, PayrollAIInsightsView
)

router = DefaultRouter()
router.register(r'profiles', PayrollProfileViewSet, basename='payrollprofile')
router.register(r'allowances', AllowanceViewSet, basename='allowance')
router.register(r'deductions', DeductionViewSet, basename='deduction')
router.register(r'payroll-runs', PayrollRunViewSet, basename='payrollrun')
router.register(r'payslips', PayslipViewSet, basename='payslip')
router.register(r'audit-logs', PayrollAuditLogViewSet, basename='auditlog')
router.register(r'salary-advances', SalaryAdvanceRequestViewSet, basename='salaryadvance')
router.register(r'bank-accounts', BankAccountViewSet, basename='bankaccount')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', PayrollAnalyticsView.as_view(), name='payroll-analytics'),
    path('ai-insights/', PayrollAIInsightsView.as_view(), name='payroll-ai-insights'),
]
