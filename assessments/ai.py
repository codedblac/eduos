import random
from typing import List, Tuple
from django.utils import timezone

from django.db.models import Avg, Count, Q
from syllabus.models import SyllabusTopic, LearningOutcome
from assessments.models import (
    Question, StudentAnswer, Assessment, AssessmentTemplate
)
from students.models import Student
from subjects.models import Subject
from classes.models import ClassLevel
from academics.models import Term


class AssessmentAIEngine:
    """
    Core AI logic for assessment generation, diagnostics, and prediction.
    """

    @staticmethod
    def suggest_questions_for_topic(topic: SyllabusTopic, count: int = 5) -> List[Question]:
        """
        Suggest random approved questions for a given topic.
        """
        return Question.objects.filter(
            topic=topic,
            type__in=['mcq', 'short', 'essay', 'code'],  # limit to deliverable types
            marks__gt=0,
            # Assume future: is_approved = True
        ).order_by('?')[:count]

    @staticmethod
    def generate_adaptive_assessment(student: Student, subject: Subject, class_level: ClassLevel, term: Term) -> List[Question]:
        """
        Generate a custom set of questions based on past weak areas and syllabus coverage.
        """
        # Get weak topics from past performance
        recent_scores = StudentAnswer.objects.filter(
            session__student=student,
            question__topic__curriculum_subject__subject=subject,
        ).values('question__topic').annotate(avg_score=Avg('marks_awarded'))

        weak_topic_ids = [r['question__topic'] for r in recent_scores if r['avg_score'] and r['avg_score'] < 50]

        # Full topic pool
        topics = SyllabusTopic.objects.filter(
            curriculum_subject__subject=subject,
            curriculum_subject__class_level=class_level,
            curriculum_subject__term=term
        )

        weak_topics = topics.filter(id__in=weak_topic_ids)
        extra_topics = topics.exclude(id__in=weak_topic_ids).order_by('?')[:max(0, 5 - weak_topics.count())]

        selected_topics = list(weak_topics) + list(extra_topics)

        # Fetch questions per topic
        questions = []
        for topic in selected_topics:
            qs = AssessmentAIEngine.suggest_questions_for_topic(topic, count=3)
            questions.extend(qs)

        return questions

    @staticmethod
    def recommend_print_delivery(assessment: Assessment) -> bool:
        """
        Suggest printing delivery if students are offline or in a remote region.
        """
        # Example heuristic: if the majority of students lack online submissions
        total_sessions = assessment.assessmentsession_set.count()
        if total_sessions == 0:
            return True  # fallback

        submitted_online = assessment.assessmentsession_set.filter(submitted_at__isnull=False).count()
        ratio = submitted_online / total_sessions
        return ratio < 0.4

    @staticmethod
    def predict_student_score(student: Student, subject: Subject) -> float:
        """
        Predict student's score in next assessment.
        """
        history = StudentAnswer.objects.filter(
            session__student=student,
            question__topic__curriculum_subject__subject=subject
        ).aggregate(avg=Avg('marks_awarded'))

        base = history['avg'] or 50
        noise = random.uniform(-5, 5)
        return round(max(0, min(100, base + noise)), 2)

    @staticmethod
    def detect_cheating_patterns(student: Student) -> List[Tuple[int, str]]:
        """
        Flag inconsistent answer patterns (basic heuristic).
        """
        suspicious = []
        answers = StudentAnswer.objects.filter(session__student=student)

        for a in answers.select_related('question'):
            difficulty = a.question.difficulty_level.lower()
            if a.marks_awarded is None:
                continue

            if difficulty == 'hard' and a.marks_awarded > 90:
                suspicious.append((a.question.id, "High score on hard question"))
            elif difficulty == 'easy' and a.marks_awarded < 40:
                suspicious.append((a.question.id, "Low score on easy question"))

        return suspicious

    @staticmethod
    def recommend_remedial_assessment(student: Student, subject: Subject) -> List[Question]:
        """
        Generate remedial questions from topics the student struggled with.
        """
        weak_topic_ids = StudentAnswer.objects.filter(
            session__student=student,
            marks_awarded__lt=50,
            question__topic__curriculum_subject__subject=subject
        ).values_list('question__topic', flat=True).distinct()

        return Question.objects.filter(
            topic_id__in=weak_topic_ids,
            marks__gt=0
        ).order_by('?')[:10]

    @staticmethod
    def nudge_teachers_on_content(subject: Subject) -> List[Tuple[str, int]]:
        """
        Identify under-covered topics needing more question content.
        """
        topics = SyllabusTopic.objects.filter(curriculum_subject__subject=subject)
        underdeveloped = []

        for topic in topics:
            q_count = Question.objects.filter(topic=topic).count()
            if q_count < 5:
                underdeveloped.append((topic.title, q_count))

        return underdeveloped

    @staticmethod
    def auto_generate_home_assessments(subject: Subject, class_level: ClassLevel, term: Term) -> Assessment:
        """
        Automatically generate a take-home or online mini assessment (e.g., CAT, Homework).
        """
        topics = SyllabusTopic.objects.filter(
            curriculum_subject__subject=subject,
            curriculum_subject__class_level=class_level,
            curriculum_subject__term=term
        ).order_by('?')[:3]

        questions = []
        for topic in topics:
            questions += list(AssessmentAIEngine.suggest_questions_for_topic(topic, count=2))

        # Create Assessment entry (not saved)
        assessment = Assessment(
            title=f"Auto CAT - {subject.name}",
            subject=subject,
            class_level=class_level,
            term=term,
            scheduled_date=timezone.now(),
            duration_minutes=30,
            total_marks=sum(q.marks for q in questions),
            is_published=False
        )
        # Optionally: Save & attach questions later
        return assessment

