# assessments/ai.py

import random
from django.db.models import Avg, Q
from syllabus.models import SyllabusTopic, LearningOutcome
from assessments.models import Question, Assessment, StudentAnswer
from students.models import Student

# --- AI Core Engine for Assessments ---

class AssessmentAIEngine:
    """
    AI engine for intelligent, curriculum-aligned, adaptive assessments.
    Powers automation for question generation, student performance prediction,
    adaptive test creation, and Bloom's taxonomy alignment.
    """

    @staticmethod
    def suggest_questions_for_topic(topic: SyllabusTopic, count: int = 5):
        """
        Suggest relevant questions for a given topic using existing tags and difficulty.
        """
        return Question.objects.filter(
            topic=topic,
            is_approved=True
        ).order_by('?')[:count]

    @staticmethod
    def generate_adaptive_assessment(student: Student, subject, class_level, term):
        """
        Generate a personalized test that adapts based on student history and topic weights.
        """
        recent_scores = StudentAnswer.objects.filter(
            student=student,
            question__subject=subject
        ).values('question__topic').annotate(avg_score=Avg('score'))

        weak_topics = [s['question__topic'] for s in recent_scores if s['avg_score'] < 50]

        # Fetch relevant topics
        topics = SyllabusTopic.objects.filter(
            curriculum_subject__subject=subject,
            curriculum_subject__class_level=class_level,
            curriculum_subject__term=term,
        )

        # Prioritize weak topics
        selected_topics = list(topics.filter(id__in=weak_topics))
        if len(selected_topics) < 5:
            remaining = topics.exclude(id__in=weak_topics)
            selected_topics += list(remaining.order_by('?')[:5 - len(selected_topics)])

        questions = []
        for topic in selected_topics:
            qs = AssessmentAIEngine.suggest_questions_for_topic(topic, count=3)
            questions.extend(qs)

        return questions

    @staticmethod
    def predict_student_score(student: Student, subject):
        """
        Predict a student's next assessment score in a subject.
        """
        history = StudentAnswer.objects.filter(
            student=student,
            question__subject=subject
        ).aggregate(avg=Avg('score'))

        base = history['avg'] if history['avg'] is not None else 50
        noise = random.uniform(-5, 5)
        predicted = max(0, min(100, base + noise))
        return round(predicted, 2)

    @staticmethod
    def detect_cheating_patterns(student: Student):
        """
        Very simple anomaly detection for inconsistent performance.
        """
        answers = StudentAnswer.objects.filter(student=student)
        inconsistencies = []

        for answer in answers:
            if answer.score > 90 and answer.question.difficulty == 'hard':
                inconsistencies.append((answer.question.id, 'Suspicious high score'))
            elif answer.score < 40 and answer.question.difficulty == 'easy':
                inconsistencies.append((answer.question.id, 'Suspicious low score'))

        return inconsistencies

    @staticmethod
    def recommend_remedial_assessment(student: Student, subject):
        """
        Generate a mini remedial assessment focused on weak learning outcomes.
        """
        weak_answers = StudentAnswer.objects.filter(
            student=student,
            score__lt=50,
            question__subject=subject
        ).values_list('question__topic', flat=True).distinct()

        questions = Question.objects.filter(
            topic_id__in=weak_answers,
            subject=subject
        ).order_by('?')[:10]

        return questions

    @staticmethod
    def nudge_teacher_on_quality(subject):
        """
        Identify topics with no or few high-quality questions to nudge teachers.
        """
        underrepresented = []
        topics = SyllabusTopic.objects.filter(curriculum_subject__subject=subject)

        for topic in topics:
            count = Question.objects.filter(topic=topic, is_approved=True).count()
            if count < 5:
                underrepresented.append((topic.title, count))

        return underrepresented

# Future additions:
# - NLP-based question generation
# - AI-powered rubrics for subjective grading
# - Smart feedback loops for learning reinforcement
