from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PayrollProfileViewSet,
    PayrollRunViewSet,
    PayslipViewSet,
    AllowanceViewSet,
    DeductionViewSet,
    SalaryAdvanceRequestViewSet,
)

router = DefaultRouter()
router.register(r'payroll-profiles', PayrollProfileViewSet, basename='payrollprofile')
router.register(r'payroll-runs', PayrollRunViewSet, basename='payrollrun')
router.register(r'payslips', PayslipViewSet, basename='payslip')
router.register(r'allowances', AllowanceViewSet, basename='allowance')
router.register(r'deductions', DeductionViewSet, basename='deduction')
router.register(r'salary-advance-requests', SalaryAdvanceRequestViewSet, basename='salaryadvancerequest')

urlpatterns = [
    path('', include(router.urls)),
]
