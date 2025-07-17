from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg
from .models import Guardian, GuardianNotification
from exams.models import ExamResult


class GuardianAnalytics:
    """
    Provides detailed insights on guardian engagement,
    student academic performance, and notification responsiveness.
    """

    def __init__(self, institution):
        self.institution = institution

    def total_guardians(self) -> int:
        return Guardian.objects.filter(institution=self.institution).count()

    def guardians_with_multiple_students(self) -> int:
        return Guardian.objects.filter(
            institution=self.institution
        ).annotate(student_count=Count("student_links")).filter(student_count__gt=1).count()

    def unread_notifications(self) -> int:
        return GuardianNotification.objects.filter(
            institution=self.institution,
            is_read=False
        ).count()

    def average_alerts_per_guardian(self) -> float:
        total_alerts = GuardianNotification.objects.filter(institution=self.institution).count()
        total_guardians = self.total_guardians()
        return round(total_alerts / total_guardians, 2) if total_guardians else 0.0

    def guardians_with_no_alerts(self) -> int:
        return Guardian.objects.filter(
            institution=self.institution
        ).annotate(alert_count=Count("notifications")).filter(alert_count=0).count()

    def guardian_response_rate(self, days: int = 30) -> float:
        cutoff = timezone.now() - timedelta(days=days)
        recent_alerts = GuardianNotification.objects.filter(
            institution=self.institution,
            timestamp__gte=cutoff
        )
        total_alerts = recent_alerts.count()
        read_alerts = recent_alerts.filter(is_read=True).count()
        return round((read_alerts / total_alerts) * 100, 2) if total_alerts else 0.0

    def student_performance_by_guardian(self):
        """
        Return a list of guardians with the average performance of their linked students.
        """
        summary = []
        guardians = Guardian.objects.filter(institution=self.institution).prefetch_related('student_links__student')

        for guardian in guardians:
            students = [link.student for link in guardian.student_links.all()]
            if not students:
                continue
            results = ExamResult.objects.filter(student__in=students)
            avg_score = results.aggregate(avg=Avg("marks"))["avg"]
            summary.append({
                "guardian": guardian.user.get_full_name(),
                "students_count": len(students),
                "average_student_score": round(avg_score, 2) if avg_score else None,
            })
        return summary

    def generate_summary(self) -> dict:
        """
        Main dashboard summary for institution admins and analytics views.
        """
        return {
            "total_guardians": self.total_guardians(),
            "multi_student_guardians": self.guardians_with_multiple_students(),
            "unread_notifications": self.unread_notifications(),
            "average_alerts_per_guardian": self.average_alerts_per_guardian(),
            "guardians_with_no_alerts": self.guardians_with_no_alerts(),
            "guardian_response_rate": self.guardian_response_rate(),
            "student_performance_summary": self.student_performance_by_guardian(),
        }
