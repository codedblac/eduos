# co_curricular/ai.py

import random
from datetime import timedelta
from django.utils import timezone
from students.models import Student
from co_curricular.models import StudentTalentProfile, ActivityParticipation, TalentCategory
from django.db.models import Count, Q


class TalentAIEngine:
    """
    AI Engine for Talent Discovery, Participation Prediction, and Activity Recommendations.
    """

    def recommend_activities_for_student(self, student: Student):
        """
        Recommend co-curricular activities to students based on past participation, interest tags,
        and gaps in talent portfolio.
        """
        participated_categories = TalentCategory.objects.filter(
            participations__student=student
        ).distinct()

        all_categories = TalentCategory.objects.all()
        untried_categories = all_categories.exclude(id__in=participated_categories)

        # Return top 3 untried categories as recommendations
        return random.sample(list(untried_categories), min(3, untried_categories.count()))

    def predict_student_engagement(self, student: Student):
        """
        Predict how actively a student will engage in the upcoming term.
        """
        participation_count = ActivityParticipation.objects.filter(
            student=student,
            date__gte=timezone.now() - timedelta(days=180)
        ).count()

        if participation_count > 10:
            return "Highly Active"
        elif participation_count > 5:
            return "Moderately Active"
        else:
            return "Low Engagement"

    def flag_underparticipating_students(self, class_level=None):
        """
        Identify students with low or no co-curricular participation.
        """
        filters = {}
        if class_level:
            filters['class_level'] = class_level

        students = Student.objects.filter(**filters)
        under_participators = []

        for student in students:
            count = ActivityParticipation.objects.filter(student=student).count()
            if count < 2:
                under_participators.append(student)

        return under_participators

    def generate_reflection_prompt(self, student: Student):
        """
        Provide AI-generated reflection prompt for student after event.
        """
        prompts = [
            f"{student.first_name}, describe what you learned from your last event.",
            "What leadership skills did you use during your recent club activity?",
            "How would you improve your performance if given a second chance?",
            "Which challenges did you face and how did you overcome them?"
        ]
        return random.choice(prompts)

    def suggest_students_for_event(self, activity_id):
        """
        Suggest students likely to excel in a given activity.
        """
        from co_curricular.models import CoCurricularActivity

        activity = CoCurricularActivity.objects.get(id=activity_id)
        similar_participations = ActivityParticipation.objects.filter(
            activity__category=activity.category
        ).values('student').annotate(freq=Count('id')).order_by('-freq')[:10]

        suggested_student_ids = [entry['student'] for entry in similar_participations]
        return Student.objects.filter(id__in=suggested_student_ids)


talent_ai = TalentAIEngine()
