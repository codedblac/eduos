from typing import Dict, List
from django.db.models import Avg, Count
import random


class TeacherAIEngine:
    """
    AI Engine for analyzing teacher performance, workload, and generating intelligent suggestions.
    """

    def __init__(self, teacher):
        self.teacher = teacher
        self.insights: List[str] = []
        self.recommendations: List[str] = []
        self.performance_score: float = 0.0
        self.feedback_summary: str = ""
        self.subject_strengths: List[str] = []

    def analyze_student_performance(self):
        """
        Aggregates average student scores per subject taught by this teacher.
        """
        from exams.models import ExamResult

        exam_data = ExamResult.objects.filter(
            subject__in=self.teacher.subjects_taught.all(),
            subject__assigned_teachers=self.teacher
        ).values('subject__name').annotate(avg_score=Avg('marks')).order_by('-avg_score')

        for result in exam_data:
            subject = result['subject__name']
            avg_score = result['avg_score'] or 0
            self.insights.append(f"Subject: {subject} | Avg Score: {avg_score:.1f}")
            if avg_score >= 70:
                self.subject_strengths.append(subject)

        if exam_data:
            self.performance_score = exam_data.aggregate(overall=Avg('avg_score'))['overall'] or 0.0

    def analyze_workload(self):
        """
        Evaluate number of lessons and streams teacher handles.
        """
        from timetable.models import TimetableEntry

        lesson_count = TimetableEntry.objects.filter(teacher=self.teacher).count()
        stream_count = self.teacher.streams_handled.count()

        self.insights.append(f"Assigned to {lesson_count} period(s) across {stream_count} stream(s).")

        if lesson_count > 30:
            self.recommendations.append("Consider reducing teaching load to avoid burnout.")

    def evaluate_feedback_summary(self):
        """
        Placeholder for student/peer feedback (extendable via AI or survey data).
        """
        sample_feedback = [
            "Highly engaging lessons",
            "Needs improvement in grading timelines",
            "Great at simplifying complex topics",
            "Encourages student participation"
        ]
        self.feedback_summary = random.choice(sample_feedback)

    def suggest_subject_alignment(self):
        """
        Recommend subjects aligned with the teacher’s strengths.
        """
        if self.subject_strengths:
            self.recommendations.append(
                f"Consider leading or mentoring in: {', '.join(self.subject_strengths)}"
            )

    def generate_insight_summary(self) -> Dict[str, any]:
        """
        Run full analysis and return structured output.
        """
        self.analyze_student_performance()
        self.analyze_workload()
        self.evaluate_feedback_summary()
        self.suggest_subject_alignment()

        return {
            "teacher": str(self.teacher),
            "performance_score": round(self.performance_score or 0, 1),
            "insights": self.insights,
            "recommendations": self.recommendations,
            "feedback_summary": self.feedback_summary
        }
