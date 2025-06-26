from datetime import datetime, timedelta, date
from django.db.models import Count, Avg, Q, F
from .models import (
    StaffHRRecord, LeaveRequest, PerformanceReview,
    DisciplinaryAction, Contract, JobApplication, JobPosting
)


class HRMAnalyticsEngine:
    """
    HRM analytics engine: staff structure, HR metrics, trends, and summaries.
    """

    def __init__(self, institution):
        self.institution = institution

    def staff_distribution_by_department(self):
        return StaffHRRecord.objects.filter(institution=self.institution)\
            .values(department_name=F('department__name'))\
            .annotate(count=Count('id'))\
            .order_by('-count')

    def staff_distribution_by_branch(self):
        return StaffHRRecord.objects.filter(institution=self.institution)\
            .values(branch_name=F('branch__name'))\
            .annotate(count=Count('id'))\
            .order_by('-count')

    def employment_type_breakdown(self):
        return StaffHRRecord.objects.filter(institution=self.institution)\
            .values('status')\
            .annotate(count=Count('id'))

    def gender_distribution(self):
        return StaffHRRecord.objects.filter(institution=self.institution)\
            .values('user__gender')\
            .annotate(count=Count('id'))

    def active_vs_inactive_staff(self):
        return StaffHRRecord.objects.filter(institution=self.institution)\
            .values('status')\
            .annotate(count=Count('id'))

    def upcoming_contract_expiry(self, within_days=30):
        today = date.today()
        deadline = today + timedelta(days=within_days)

        return Contract.objects.filter(
            staff__institution=self.institution,
            end_date__range=(today, deadline),
            is_active=True
        ).values(
            first_name=F('staff__user__first_name'),
            last_name=F('staff__user__last_name'),
            end_date=F('end_date'),
            designation=F('staff__designation')
        )

    def average_performance_by_department(self):
        return PerformanceReview.objects.filter(
            staff__institution=self.institution
        ).values(department_name=F('staff__department__name'))\
         .annotate(avg_score=Avg('score'))\
         .order_by('-avg_score')

    def most_disciplined_staff(self, limit=10):
        return DisciplinaryAction.objects.filter(
            staff__institution=self.institution
        ).values(
            first_name=F('staff__user__first_name'),
            last_name=F('staff__user__last_name')
        ).annotate(count=Count('id')).order_by('-count')[:limit]

    def leave_usage_trend(self, year=None):
        year = year or datetime.today().year

        return LeaveRequest.objects.filter(
            staff__institution=self.institution,
            start_date__year=year,
            status='approved'
        ).annotate(month=F('start_date__month'))\
         .values('month')\
         .annotate(total=Count('id'))\
         .order_by('month')

    def job_applications_summary(self):
        return JobApplication.objects.filter(
            job__department__branch__institution=self.institution
        ).values(job_title=F('job__title'))\
         .annotate(total=Count('id'))\
         .order_by('-total')

    def current_summary(self):
        """
        Returns current HRM summary stats for dashboard.
        """
        return {
            "total_staff": StaffHRRecord.objects.filter(institution=self.institution).count(),
            "active_staff": StaffHRRecord.objects.filter(institution=self.institution, status='active').count(),
            "vacancies": JobPosting.objects.filter(department__branch__institution=self.institution).count(),
            "expiring_contracts": list(self.upcoming_contract_expiry()),
            "gender_distribution": list(self.gender_distribution()),
            "department_distribution": list(self.staff_distribution_by_department()),
            "leave_trend": list(self.leave_usage_trend())
        }
