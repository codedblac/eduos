from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q, Avg
from .models import Guardian, GuardianNotification, GuardianStudentLink
from students.models import Student
from exams.models import ExamResult


class GuardianAnalytics:
    """
    Provides data insights and analytical summaries about guardian engagement,
    alerts responsiveness, and student-linked academic performance.
    """

    def __init__(self, institution):
        self.institution = institution

    def total_guardians(self):
        return Guardian.objects.filter(institution=self.institution).count()

    def guardians_with_multiple_students(self):
        return Guardian.objects.filter(
            institution=self.institution,
            student_links__isnull=False
        ).annotate(num_students=Count("student_links")).filter(num_students__gt=1).count()

    def unread_notifications(self):
        return GuardianNotification.objects.filter(
            institution=self.institution,
            is_read=False
        ).count()

    def average_alerts_per_guardian(self):
        total_alerts = GuardianNotification.objects.filter(institution=self.institution).count()
        total_guardians = self.total_guardians()
        return round(total_alerts / total_guardians, 2) if total_guardians else 0

    def guardians_with_no_alerts(self):
        return Guardian.objects.filter(
            institution=self.institution
        ).annotate(alert_count=Count("notifications")).filter(alert_count=0).count()

    def guardian_response_rate(self, days=30):
        recent_cutoff = timezone.now() - timedelta(days=days)
        recent_alerts = GuardianNotification.objects.filter(
            institution=self.institution,
            timestamp__gte=recent_cutoff
        )
        read_count = recent_alerts.filter(is_read=True).count()
        total = recent_alerts.count()
        return round((read_count / total) * 100, 2) if total > 0 else 0.0

    def student_performance_by_guardian(self):
        # Analyze average student performance per guardian
        data = []
        guardians = Guardian.objects.filter(institution=self.institution).prefetch_related('student_links__student')
        for guardian in guardians:
            students = [link.student for link in guardian.student_links.all()]
            results = ExamResult.objects.filter(student__in=students)
            avg_score = results.aggregate(Avg("marks"))["marks__avg"]
            data.append({
                "guardian": guardian.user.get_full_name(),
                "students_count": len(students),
                "average_student_score": round(avg_score, 2) if avg_score else None
            })
        return data

    def generate_summary(self):
        return {
            "total_guardians": self.total_guardians(),
            "multi_student_guardians": self.guardians_with_multiple_students(),
            "unread_notifications": self.unread_notifications(),
            "average_alerts_per_guardian": self.average_alerts_per_guardian(),
            "guardians_with_no_alerts": self.guardians_with_no_alerts(),
            "guardian_response_rate": self.guardian_response_rate(),
            "student_performance_summary": self.student_performance_by_guardian(),
        }
