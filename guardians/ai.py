from typing import Dict, Any, List
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg
from .models import Guardian, GuardianNotification
from exams.models import ExamResult


class GuardianAIEngine:
    """
    AI engine for personalized guardian insights, alerts, and recommendations.
    Provides intelligent summaries for guardians regarding their linked students.
    """

    def __init__(self, guardian: Guardian):
        self.guardian = guardian
        self.students = guardian.student_links.select_related('student').all()
        self.alerts: List[str] = []
        self.recommendations: List[str] = []

    def fetch_recent_alerts(self, days: int = 30) -> List[GuardianNotification]:
        """
        Retrieve recent notifications for the guardian within the past X days.
        """
        cutoff = timezone.now() - timedelta(days=days)
        return GuardianNotification.objects.filter(
            guardian=self.guardian,
            timestamp__gte=cutoff
        ).order_by('-timestamp')

    def summarize_student_academics(self):
        """
        Analyze recent academic performance for each student linked to the guardian.
        """
        for link in self.students:
            student = link.student
            recent_results = ExamResult.objects.filter(student=student).order_by('-exam__date')[:5]
            if recent_results.exists():
                avg_score = recent_results.aggregate(Avg("marks"))["marks__avg"] or 0.0
                self.alerts.append(f"📘 {student.get_full_name()}'s recent average: {avg_score:.2f}%")
                if avg_score < 50:
                    self.recommendations.append(f"⚠️ Consider academic support for {student.get_full_name()}.")
                elif avg_score > 80:
                    self.recommendations.append(f"🎯 Encourage {student.get_full_name()} to explore advanced learning programs.")
            else:
                self.alerts.append(f"ℹ️ No recent exam results available for {student.get_full_name()}.")

    def summarize_guardian_notifications(self):
        """
        Summarize unread alerts for the guardian.
        """
        recent_alerts = self.fetch_recent_alerts()
        unread_count = recent_alerts.filter(is_read=False).count()
        if unread_count:
            self.alerts.append(f"🔔 You have {unread_count} unread school notification(s).")

    def generate_feedback(self) -> Dict[str, Any]:
        """
        Run AI evaluation and return a structured summary of alerts and recommendations.
        """
        self.summarize_student_academics()
        self.summarize_guardian_notifications()

        return {
            "guardian": self.guardian.user.get_full_name(),
            "alerts": self.alerts,
            "recommendations": self.recommendations,
        }

    def run_analysis(self) -> Dict[str, Any]:
        """
        Entry point for full analysis.
        """
        return self.generate_feedback()
