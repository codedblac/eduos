# staff/analytics.py

from django.db.models import Count, Q, Avg
from datetime import timedelta
from django.utils import timezone
from .models import Staff, StaffAttendance
from departments.models import Department

class StaffAnalytics:
    def __init__(self, institution):
        self.institution = institution

    def staff_distribution_by_type(self):
        """
        Returns staff count grouped by type (teaching/non-teaching/support)
        """
        return {
            "teaching": Staff.objects.filter(institution=self.institution, is_teaching=True).count(),
            "non_teaching": Staff.objects.filter(institution=self.institution, is_teaching=False).count(),
            "support": Staff.objects.filter(institution=self.institution, staff_type='support').count()
        }

    def staff_count_by_department(self):
        """
        Returns a breakdown of staff count per department
        """
        return list(
            Department.objects.filter(institution=self.institution).annotate(
                total_staff=Count('members')
            ).values('name', 'total_staff')
        )

    def attendance_trend_last_30_days(self):
        """
        Returns daily attendance counts for the last 30 days
        """
        today = timezone.now().date()
        days = [today - timedelta(days=i) for i in range(29, -1, -1)]
        result = []

        for day in days:
            daily_present = StaffAttendance.objects.filter(
                staff__institution=self.institution,
                date=day,
                status='present'
            ).count()
            result.append({
                "date": day,
                "present": daily_present
            })

        return result

    def average_attendance_rate(self):
        """
        Calculates average staff attendance rate over the past 30 days
        """
        today = timezone.now().date()
        month_ago = today - timedelta(days=30)
        attendance = StaffAttendance.objects.filter(
            staff__institution=self.institution,
            date__range=(month_ago, today)
        )

        total = attendance.count()
        present = attendance.filter(status='present').count()

        return round((present / total) * 100, 2) if total > 0 else 0

    def top_absentees(self, limit=5):
        """
        Returns staff with highest absences in the last 30 days
        """
        month_ago = timezone.now().date() - timedelta(days=30)
        return list(
            Staff.objects.filter(institution=self.institution).annotate(
                absence_count=Count('attendance_records', filter=Q(attendance_records__status='absent', attendance_records__date__gte=month_ago))
            ).filter(absence_count__gt=0).order_by('-absence_count')[:limit].values('user__first_name', 'user__last_name', 'absence_count')
        )

    def department_performance_snapshot(self):
        """
        Placeholder: Would pull subject-level performance metrics
        Requires integration with exams app
        """
        # Example structure for future
        return [
            {
                "department": "Sciences",
                "average_score": 68.4,
                "underperforming_subjects": 2
            },
            {
                "department": "Humanities",
                "average_score": 72.9,
                "underperforming_subjects": 0
            }
        ]
