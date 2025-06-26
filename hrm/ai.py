from datetime import date, timedelta
from django.db.models import Count, Avg, Q
from .models import (
    StaffHRRecord, JobApplication, PerformanceReview,
    Contract, LeaveRequest, DisciplinaryAction
)


class HRMAIEngine:
    """
    AI engine for smart HR insights: recruitment, performance,
    attrition risk, contract alerts, and leave trends.
    """

    def __init__(self, institution):
        self.institution = institution

    def shortlist_best_applicants(self, vacancy_id, top_n=5):
        """
        Ranks applicants based on qualification match and experience years.
        """
        apps = JobApplication.objects.filter(job__id=vacancy_id, job__department__branch__institution=self.institution)

        # Example heuristic: weight experience and qualifications equally
        ranked = sorted(apps, key=lambda a: (
            (getattr(a, 'years_of_experience', 0) or 0) + (1 if getattr(a, 'qualification_level', '') in ['Masters', 'PhD'] else 0)
        ), reverse=True)

        return ranked[:top_n]

    def detect_performance_anomalies(self):
        """
        Identifies staff with performance score drops over time.
        """
        flagged = []
        for staff in StaffHRRecord.objects.filter(institution=self.institution):
            reviews = PerformanceReview.objects.filter(staff=staff).order_by('-review_period_end')[:4]
            scores = [r.score for r in reviews if r.score is not None]

            if len(scores) >= 2:
                avg_previous = sum(scores[1:]) / len(scores[1:])
                if avg_previous and abs(scores[0] - avg_previous) / avg_previous > 0.3:
                    flagged.append({
                        "staff": staff.user.get_full_name(),
                        "recent_score": scores[0],
                        "previous_avg": round(avg_previous, 2),
                        "anomaly": "Significant score fluctuation"
                    })
        return flagged

    def expiring_contracts_alerts(self, within_days=30):
        """
        Contracts nearing expiry within N days.
        """
        today = date.today()
        deadline = today + timedelta(days=within_days)

        contracts = Contract.objects.filter(
            staff__institution=self.institution,
            end_date__range=(today, deadline),
            is_active=True
        )

        return [
            {
                "staff": contract.staff.user.get_full_name(),
                "contract_end": contract.end_date,
                "position": contract.staff.designation
            }
            for contract in contracts
        ]

    def leave_balance_issues(self, threshold=3):
        """
        Detects staff with dangerously low leave balance.
        """
        risky = []
        for staff in StaffHRRecord.objects.filter(institution=self.institution):
            approved_leaves = LeaveRequest.objects.filter(staff=staff, status='approved')
            used_days = sum((leave.end_date - leave.start_date).days for leave in approved_leaves)

            # Assume leave_entitlement field exists, else default to 30
            entitlement = getattr(staff, 'leave_entitlement', 30)
            balance = entitlement - used_days

            if balance <= threshold:
                risky.append({
                    "staff": staff.user.get_full_name(),
                    "leave_balance": balance
                })
        return risky

    def predict_attrition_risk(self):
        """
        Heuristic attrition model: low performance + high leave + past warnings.
        """
        at_risk = []

        for staff in StaffHRRecord.objects.filter(institution=self.institution):
            reviews = PerformanceReview.objects.filter(staff=staff)
            leaves = LeaveRequest.objects.filter(staff=staff, status='approved')
            warnings_count = DisciplinaryAction.objects.filter(staff=staff).count()

            avg_score = reviews.aggregate(avg=Avg('score'))['avg'] or 0
            leave_days = sum((leave.end_date - leave.start_date).days for leave in leaves)

            risk = 0
            if avg_score < 3:
                risk += 1
            if leave_days > 30:
                risk += 1
            if warnings_count >= 2:
                risk += 1

            if risk >= 2:
                at_risk.append({
                    "staff": staff.user.get_full_name(),
                    "risk_score": risk,
                    "note": "Potential attrition risk"
                })

        return at_risk
