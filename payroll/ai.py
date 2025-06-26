# payroll/ai.py

from django.db.models import Sum, Avg
from datetime import date
from .models import Payslip, PayrollProfile, SalaryAdvanceRequest
from staff.models import StaffProfile


class PayrollAIEngine:
    """
    AI engine for payroll pattern detection, salary recommendation,
    fraud alerts, and staff-level salary anomaly identification.
    """

    def __init__(self, institution):
        self.institution = institution

    def detect_salary_anomalies(self):
        """
        Identify staff with unexpected salary fluctuations (>30% from average).
        """
        anomalies = []
        profiles = PayrollProfile.objects.filter(staff_profile__institution=self.institution)
        for profile in profiles:
            payslips = Payslip.objects.filter(
                staff_profile=profile.staff_profile
            ).order_by('-generated_on')[:6]
            if payslips.count() >= 2:
                values = [float(p.net_pay) for p in payslips if p.net_pay]
                if len(values) > 1:
                    avg_net = sum(values[1:]) / len(values[1:])
                    if avg_net and abs(values[0] - avg_net) / avg_net > 0.3:
                        anomalies.append({
                            "staff": profile.staff_profile.user.get_full_name(),
                            "latest_salary": values[0],
                            "previous_avg": round(avg_net, 2),
                            "difference": round(abs(values[0] - avg_net), 2)
                        })
        return anomalies

    def recommend_salary_scale(self, department=None):
        """
        Suggest average salary by designation or department for benchmarking.
        """
        qs = PayrollProfile.objects.filter(staff_profile__institution=self.institution)
        if department:
            qs = qs.filter(staff_profile__department=department)

        recommendations = qs.values('staff_profile__designation').annotate(
            average_salary=Avg('basic_salary')
        ).order_by('-average_salary')

        return [
            {
                "designation": item['staff_profile__designation'],
                "average_salary": round(item['average_salary'], 2) if item['average_salary'] else None
            } for item in recommendations
        ]

    def flag_overtime_abuse(self):
        """
        Detect departments with consistently inflated pay (e.g., exaggerated overtime).
        """
        flagged = []
        for dept in self.institution.departments.all():
            gross_avg = Payslip.objects.filter(
                staff_profile__department=dept
            ).aggregate(avg=Avg('gross_salary'))['avg'] or 0

            if gross_avg > 180000:  # Example benchmark
                flagged.append({
                    "department": dept.name,
                    "average_gross": round(gross_avg, 2),
                    "note": "Possible allowance or overtime inflation."
                })
        return flagged

    def predict_payslip_errors(self):
        """
        Heuristic checks for potential errors in current month's payroll.
        """
        current_month = date.today().month
        current_year = date.today().year

        payslips = Payslip.objects.filter(
            payroll_run__period_start__month=current_month,
            payroll_run__period_start__year=current_year,
            staff_profile__institution=self.institution
        )

        errors = []
        for payslip in payslips:
            if payslip.net_pay < 5000 or payslip.gross_salary == 0:
                errors.append({
                    "staff": payslip.staff_profile.user.get_full_name(),
                    "reason": "Unusually low net pay or zero gross salary.",
                    "net_salary": float(payslip.net_pay),
                    "gross_salary": float(payslip.gross_salary)
                })
        return errors

    def predict_advance_risk(self):
        """
        Identify staff with excessive salary advance requests.
        """
        high_risk = []
        advances = SalaryAdvanceRequest.objects.filter(
            staff_profile__institution=self.institution,
            status='approved'
        )

        staff_totals = advances.values('staff_profile').annotate(total_advanced=Sum('amount')).order_by('-total_advanced')

        for entry in staff_totals:
            if entry['total_advanced'] > 100000:
                staff = StaffProfile.objects.get(id=entry['staff_profile'])
                high_risk.append({
                    "staff": staff.user.get_full_name(),
                    "advance_total": entry['total_advanced'],
                    "risk": "Possible financial distress or dependency on advances."
                })
        return high_risk
