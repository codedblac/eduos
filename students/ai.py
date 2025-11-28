from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Avg, Q, Count
from exams.models import ExamResult
from e_library.models import ELibraryResource
from teachers.models import Teacher
from students.models import Student
from classes.models import ClassLevel, Stream
import random


class StudentAIAnalyzer:
    """
    Advanced AI engine for analyzing student performance,
    recommending books, mentors, stream allocation, and personalized feedback.
    """

    def __init__(self, student: Student):
        self.student = student
        self.performance_data = {}
        self.insights = []
        self.suggestions = []
        self.feedback = []
        self.feedback_comment = ""

    def fetch_recent_exam_results(self, months=6) -> List[ExamResult]:
        since_date = datetime.now() - timedelta(days=30 * months)
        return ExamResult.objects.filter(
            student=self.student,
            exam__date__gte=since_date
        ).select_related('subject').order_by('exam__date')

    def analyze_performance_trends(self):
        results = self.fetch_recent_exam_results()
        if not results:
            self.insights.append("No recent exam results available.")
            return

        subject_scores = defaultdict(list)
        for res in results:
            subject_scores[res.subject.name].append((res.exam.date, res.marks))

        for subject, scores in subject_scores.items():
            mid = len(scores) // 2 or 1
            first_avg = sum(m for _, m in scores[:mid]) / mid
            second_avg = sum(m for _, m in scores[mid:]) / (len(scores) - mid or 1)

            if second_avg > first_avg + 5:
                self.insights.append(f"Improving in {subject}. Keep it up!")
                self.feedback.append(f"Strong improvement seen in {subject}.")
            elif second_avg < first_avg - 5:
                self.insights.append(f"Declining in {subject}. Needs attention.")
                self.feedback.append(f"Drop in {subject} performance. Practice recommended.")
                self.suggestions.extend(self._suggest_resources(subject))
            else:
                self.insights.append(f"Stable performance in {subject}.")
                self.feedback.append(f"{subject} performance steady.")

    def _suggest_resources(self, subject_name: str) -> List[str]:
        materials = ELibraryResource.objects.filter(
            Q(subject__name__icontains=subject_name),
            access_level='public'
        ).order_by('-rating')[:3]

        teachers = Teacher.objects.filter(
            Q(subjects_taught__name__icontains=subject_name),
            institution=self.student.institution
        ).order_by('-rating')[:3]

        suggestions = []
        if materials.exists():
            suggestions.append("📚 Suggested resources:")
            suggestions.extend([f"- {m.title}" for m in materials])
        if teachers.exists():
            suggestions.append("👨‍🏫 Consider help from:")
            suggestions.extend([f"- {t.user.get_full_name()}" for t in teachers])

        return suggestions

    def generate_personalized_comment(self):
        name = self.student.first_name
        self.feedback_comment = f"Performance summary for {name}:\n"
        self.feedback_comment += "\n".join(self.feedback or ["No feedback available."])
        if self.suggestions:
            self.feedback_comment += "\n\nSuggestions:\n" + "\n".join(self.suggestions)

    def recommend_books(self):
        options = [
            "Growth Mindset Workbook", "STEAM Projects for Kids",
            "Creative Reading Essentials", "National Curriculum Practice Tests"
        ]
        self.student.recommended_books = random.sample(options, 2)
        self.student.save(update_fields = ['recommended_books'])
        return self.student.recommended_books

    def recommend_mentors(self):
        teachers = Teacher.objects.filter(institution=self.student.institution)
        if teachers.exists():
            top_choices = random.sample(list(teachers.values_list('user__first_name', flat=True)), k=min(2, teachers.count()))
            self.student.recommended_teachers = top_choices
            self.student.save(update_fields = ['recommended_teachers'])
            return top_choices
        return []

    def auto_assign_stream(self):
        if not self.student.class_level:
            return None
        streams = self.student.class_level.streams.annotate(student_count=Count('students')).order_by('student_count')
        if streams.exists():
            self.student.stream = streams.first()
            self.student.save(update_fields = ['stream'])
            return self.student.stream
        return None

    def generate_summary(self):
        self.student.ai_insights = f"{self.student.first_name} is currently in {self.student.class_level} - {self.student.stream}."
        self.student.performance_comments = self.feedback_comment
        self.student.save(update_fields = ['ai_insights', 'performance_comments'])

    def run_full_analysis(self) -> Dict[str, Any]:
        self.analyze_performance_trends()
        self.generate_personalized_comment()
        self.recommend_books()
        self.recommend_mentors()
        self.auto_assign_stream()
        self.generate_summary()

        return {
            "insights": self.insights,
            "suggestions": self.suggestions,
            "feedback_comment": self.feedback_comment,
        }
