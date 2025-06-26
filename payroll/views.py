# payroll/views.py

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    PayrollProfile, PayrollRun, Payslip,
    Allowance, Deduction, SalaryAdvanceRequest
)
from .serializers import (
    PayrollProfileSerializer, PayrollRunSerializer, PayslipSerializer,
    AllowanceSerializer, DeductionSerializer, SalaryAdvanceRequestSerializer
)
from .permissions import (
    IsHRManager, IsFinanceManager, IsStaffOrReadOnly
)
from .filters import (
    PayrollProfileFilter, PayrollRunFilter, PayslipFilter,
    AllowanceFilter, DeductionFilter, SalaryAdvanceRequestFilter
)
from .analytics import PayrollAnalyticsEngine
from .ai import PayrollAIEngine


class PayrollProfileViewSet(viewsets.ModelViewSet):
    queryset = PayrollProfile.objects.select_related('staff_profile', 'staff_profile__department').all()
    serializer_class = PayrollProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PayrollProfileFilter
    search_fields = ['staff_profile__user__first_name', 'staff_profile__user__last_name', 'staff_profile__designation']


class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.prefetch_related('payslips').all()
    serializer_class = PayrollRunSerializer
    permission_classes = [permissions.IsAuthenticated, IsFinanceManager]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PayrollRunFilter
    ordering_fields = ['period_start', 'period_end', 'processed_on']

    @action(detail=True, methods=['post'], permission_classes=[IsFinanceManager])
    def lock(self, request, pk=None):
        run = self.get_object()
        run.is_locked = True
        run.save()
        return Response({"detail": "Payroll run locked."})

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        engine = PayrollAnalyticsEngine(institution=request.user.institution)
        data = engine.current_payroll_summary()
        return Response(data)

    @action(detail=False, methods=['get'])
    def anomalies(self, request):
        engine = PayrollAIEngine(institution=request.user.institution)
        anomalies = engine.detect_salary_anomalies()
        return Response(anomalies)


class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.select_related('staff_profile', 'payroll_run').all()
    serializer_class = PayslipSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PayslipFilter
    search_fields = ['staff_profile__user__first_name', 'staff_profile__user__last_name']

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        # Placeholder for payslip PDF generation
        return Response({"detail": "PDF download logic placeholder."})


class AllowanceViewSet(viewsets.ModelViewSet):
    queryset = Allowance.objects.select_related('staff_profile').all()
    serializer_class = AllowanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AllowanceFilter


class DeductionViewSet(viewsets.ModelViewSet):
    queryset = Deduction.objects.select_related('staff_profile').all()
    serializer_class = DeductionSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DeductionFilter


class SalaryAdvanceRequestViewSet(viewsets.ModelViewSet):
    queryset = SalaryAdvanceRequest.objects.select_related('staff_profile').all()
    serializer_class = SalaryAdvanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SalaryAdvanceRequestFilter

    @action(detail=True, methods=['post'], permission_classes=[IsFinanceManager])
    def approve(self, request, pk=None):
        advance = self.get_object()
        advance.status = SalaryAdvanceRequest.APPROVED
        advance.save()
        return Response({'status': 'Advance approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsFinanceManager])
    def reject(self, request, pk=None):
        advance = self.get_object()
        advance.status = SalaryAdvanceRequest.REJECTED
        advance.save()
        return Response({'status': 'Advance rejected'})
