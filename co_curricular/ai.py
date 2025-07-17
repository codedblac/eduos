import random
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q

from students.models import Student
from co_curricular.models import (
    StudentProfile,
    StudentActivityParticipation,
    Activity,
    ActivityCategory,
)


class TalentAIEngine:
    """
    AI Engine for Talent Discovery, Participation Prediction, and Activity Recommendations.
    """

    def recommend_activities_for_student(self, student: Student):
        """
        Recommend co-curricular activities to a student based on:
        - Past participation
        - Gaps in category exposure
        """
        participated_categories = ActivityCategory.objects.filter(
            activity__studentactivityparticipation__student=student
        ).distinct()

        all_categories = ActivityCategory.objects.all()
        untried_categories = all_categories.exclude(id__in=participated_categories)

        # Randomized but controlled suggestion
        return random.sample(list(untried_categories), min(3, untried_categories.count()))

    def predict_student_engagement(self, student: Student):
        """
        Predict student engagement level over the past 6 months.
        """
        recent_participations = StudentActivityParticipation.objects.filter(
            student=student,
            joined_on__gte=timezone.now() - timedelta(days=180)
        ).count()

        if recent_participations > 10:
            return "Highly Active"
        elif recent_participations > 5:
            return "Moderately Active"
        else:
            return "Low Engagement"

    def flag_underparticipating_students(self, class_level=None):
        """
        Identify students with low or no participation in co-curriculars.
        """
        filters = {}
        if class_level:
            filters['current_class'] = class_level

        students = Student.objects.filter(**filters)
        under_participators = []

        for student in students:
            count = StudentActivityParticipation.objects.filter(student=student).count()
            if count < 2:
                under_participators.append(student)

        return under_participators

    def generate_reflection_prompt(self, student: Student):
        """
        AI-generated reflective prompt to encourage thoughtful journaling.
        """
        prompts = [
            f"{student.first_name}, describe what you learned from your last activity or event.",
            "What leadership skills did you demonstrate recently?",
            "What would you do differently if given another chance?",
            "Which challenges did you face and how did you respond?",
            "How did your participation help your team or club succeed?",
        ]
        return random.choice(prompts)

    def suggest_students_for_event(self, activity_id):
        """
        Suggest high-potential students for a given activity based on category history.
        """
        activity = Activity.objects.get(id=activity_id)

        # Look for students who have frequent participation in the same category
        similar_participations = StudentActivityParticipation.objects.filter(
            activity__category=activity.category
        ).values('student').annotate(freq=Count('id')).order_by('-freq')[:10]

        suggested_ids = [entry['student'] for entry in similar_participations]
        return Student.objects.filter(id__in=suggested_ids)


talent_ai = TalentAIEngine()
