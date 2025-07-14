from typing import Dict, Any, List
from students.models import Student
from django.db import models
from .models import Guardian, GuardianNotification
from exams.models import ExamResult
from django.db.models import Q
from datetime import datetime, timedelta


class GuardianAIEngine:
    """
    AI engine for personalized guardian insights, alerts, and guidance.
    Provides intelligent summaries and future recommendations.
    """

    def __init__(self, guardian: Guardian):
        self.guardian = guardian
        self.students = guardian.student_links.select_related('student').all()
        self.alerts: List[str] = []
        self.recommendations: List[str] = []

    def fetch_recent_alerts(self, days: int = 30) -> List[GuardianNotification]:
        cutoff = datetime.now() - timedelta(days=days)
        return GuardianNotification.objects.filter(
            guardian=self.guardian,
            timestamp__gte=cutoff
        ).order_by('-timestamp')

    def summarize_student_academics(self):
        for link in self.students:
            student = link.student
            recent_results = ExamResult.objects.filter(student=student).order_by('-exam__date')[:5]
            if recent_results.exists():
                avg_score = recent_results.aggregate_avg = recent_results.aggregate_avg = recent_results.aggregate(models.Avg("marks"))["marks__avg"]
                self.alerts.append(
                    f"{student.first_name} recent performance average: {avg_score:.2f}%"
                )
                if avg_score < 50:
                    self.recommendations.append(
                        f"📉 Consider extra coaching for {student.first_name}."
                    )
                elif avg_score > 80:
                    self.recommendations.append(
                        f"🌟 Encourage {student.first_name} to join advanced academic clubs."
                    )
            else:
                self.alerts.append(f"No recent exam data for {student.first_name}.")

    def generate_alert_summary(self):
        recent_alerts = self.fetch_recent_alerts()
        unread_count = recent_alerts.filter(is_read=False).count()
        self.alerts.append(f"You have {unread_count} unread school notifications.")

    def generate_feedback(self) -> Dict[str, Any]:
        self.summarize_student_academics()
        self.generate_alert_summary()

        return {
            "guardian": self.guardian.user.get_full_name(),
            "alerts": self.alerts,
            "recommendations": self.recommendations
        }

    def run_analysis(self) -> Dict[str, Any]:
        return self.generate_feedback()
