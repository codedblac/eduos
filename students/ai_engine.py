# students/ai_engine.py

from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Avg, Q
from exams.models import ExamResult
from e_library.models import ELibraryResource
from teachers.models import Teacher
from students.models import Student

class StudentAIAnalyzer:
    """
    Advanced AI engine for analyzing student performance,
    generating insights, feedback, and suggestions.
    """

    def __init__(self, student: Student):
        self.student = student
        self.performance_data = {}
        self.insights = []
        self.suggestions = []
        self.feedback = []

    def fetch_recent_exam_results(self, months=6) -> List[ExamResult]:
        since_date = datetime.now() - timedelta(days=30 * months)
        return ExamResult.objects.filter(
            student=self.student,
            exam__date__gte=since_date
        ).select_related('subject').order_by('exam__date')

    def analyze_performance_trends(self):
        results = self.fetch_recent_exam_results()
        if not results:
            self.insights.append("No recent exam results available to analyze.")
            return

        # Group marks by subject and sort by exam date
        subject_scores = defaultdict(list)
        for res in results:
            subject_scores[res.subject.name].append((res.exam.date, res.marks))

        trend_messages = []
        for subject, scores in subject_scores.items():
            # Calculate average marks for first half and second half of period
            mid_index = len(scores) // 2 or 1
            first_half_avg = sum(m for _, m in scores[:mid_index]) / mid_index
            second_half_avg = sum(m for _, m in scores[mid_index:]) / (len(scores) - mid_index or 1)

            # Detect trend
            if second_half_avg > first_half_avg + 5:
                trend_messages.append(f"Improving in {subject}. Keep it up!")
                self.feedback.append(f"Great improvement observed in {subject}.")
            elif second_half_avg < first_half_avg - 5:
                trend_messages.append(f"Declining performance in {subject}. Needs attention.")
                self.feedback.append(f"Performance decline detected in {subject}. Consider extra practice.")
                self.suggestions.extend(self._suggest_resources(subject))
            else:
                trend_messages.append(f"Stable performance in {subject}.")
                self.feedback.append(f"Performance stable in {subject}.")

        self.insights.extend(trend_messages)

    def _suggest_resources(self, subject_name: str) -> List[str]:
        # Find library materials and teachers specialized in this subject
        materials = ELibraryResource.objects.filter(
            Q(subject__name__icontains=subject_name) &
            Q(access_level='public')  # Public library materials for all students
        ).order_by('-rating')[:3]

        teachers = Teacher.objects.filter(
            Q(subjects_taught__name__icontains=subject_name) &
            Q(teacher__institution=self.student.institution)
        ).order_by('-rating')[:3]

        suggestions = []
        if materials.exists():
            suggestions.append("Recommended books/materials:")
            suggestions.extend([f"- {mat.title}" for mat in materials])
        if teachers.exists():
            suggestions.append("Consider extra help from these teachers:")
            suggestions.extend([f"- {t.teacher.user.get_full_name()}" for t in teachers])

        return suggestions

    def generate_personalized_comment(self):
        # Summarize performance feedback and suggestions into a comment
        comment = f"Performance report for {self.student.user.get_full_name()}:\n\n"
        if not self.feedback:
            comment += "No significant data available to generate comments."
        else:
            comment += "\n".join(self.feedback)
        if self.suggestions:
            comment += "\n\nSuggestions:\n" + "\n".join(self.suggestions)
        self.feedback_comment = comment

    def run_full_analysis(self) -> Dict[str, Any]:
        self.analyze_performance_trends()
        self.generate_personalized_comment()
        return {
            "insights": self.insights,
            "suggestions": self.suggestions,
            "feedback_comment": getattr(self, 'feedback_comment', '')
        }
