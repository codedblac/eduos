# exams/ai.py

import random
from datetime import datetime
from collections import defaultdict
from django.db.models import Avg, Count

from syllabus.models import SyllabusTopic
from exams.models import (
    Exam, ExamSubject, ExamPrediction,
    ExamInsight, StudentScore, ExamResult
)
from students.models import Student
from subjects.models import Subject
from teachers.models import Teacher

USE_NLP_AI = False  # Placeholder for future OpenAI integration


class ExamAIEngine:
    """
    AI engine for automating and assisting exam workflows.
    Supports:
    - Predictive performance and weak areas
    - Topic-based question generation
    - Workload insights
    - Streamlined exam prediction
    """

    @staticmethod
    def predict_weak_topics(subject, class_level, term):
        """
        Identify underperforming topics for reinforcement.
        """
        weak_topics = []

        scores = StudentScore.objects.filter(
            exam_subject__subject=subject,
            exam_subject__exam__class_level=class_level,
            exam_subject__exam__term=term
        ).values('exam_subject__subject').annotate(avg_score=Avg('score'))

        for entry in scores:
            if entry['avg_score'] is not None and entry['avg_score'] < 50:
                weak_topics.append(entry['exam_subject__subject'])

        return weak_topics

    @staticmethod
    def recommend_topics_from_syllabus(subject, class_level, term):
        """
        Recommend syllabus topics for subject/class/term.
        """
        return SyllabusTopic.objects.filter(
            curriculum_subject__subject=subject,
            curriculum_subject__class_level=class_level,
            curriculum_subject__term=term
        )

    @staticmethod
    def generate_exam_questions(topics, difficulty_mix=(0.4, 0.4, 0.2), question_pool=None):
        """
        Generate exam questions based on difficulty distribution.
        """
        question_pool = question_pool or {}
        selected = []

        for topic in topics:
            questions = question_pool.get(topic.id) or topic.questions.all()

            easy = [q for q in questions if q.difficulty_level == 'easy']
            medium = [q for q in questions if q.difficulty_level == 'medium']
            hard = [q for q in questions if q.difficulty_level == 'hard']

            selected.extend(random.sample(easy, min(len(easy), max(1, int(difficulty_mix[0] * 5)))))
            selected.extend(random.sample(medium, min(len(medium), max(1, int(difficulty_mix[1] * 5)))))
            selected.extend(random.sample(hard, min(len(hard), max(1, int(difficulty_mix[2] * 5)))))

        return selected

    @staticmethod
    def auto_generate_exam(subject, class_level, term, stream, institution, teacher=None, year=None):
        """
        Generate a full exam paper with AI support.
        """
        year = year or datetime.now().year
        topics = ExamAIEngine.recommend_topics_from_syllabus(subject, class_level, term)
        questions = ExamAIEngine.generate_exam_questions(topics)

        predicted_questions = [{"text": q.text, "marks": q.marks, "type": q.type} for q in questions]

        exam = ExamPrediction.objects.create(
            subject=subject,
            class_level=class_level,
            term=term,
            stream=stream,
            institution=institution,
            predicted_questions=predicted_questions,
            source_summary="Generated from syllabus and performance analytics.",
            created_by=teacher.user if teacher else None
        )

        return exam

    @staticmethod
    def generate_marking_scheme(questions):
        """
        Generate a textual marking scheme for AI-generated exam.
        """
        return "\n".join([
            f"{i + 1}. {q['text'][:40]}... [{q['marks']} Marks]"
            for i, q in enumerate(questions)
        ])

    @staticmethod
    def predict_student_performance(student, subject):
        """
        Predict student performance using past averages.
        """
        result = ExamResult.objects.filter(
            student=student,
            exam__subjects__subject=subject
        ).aggregate(avg=Avg('average_score'))

        base = result['avg'] or 50
        return round(min(100, max(0, base + random.uniform(-5, 5))), 2)

    @staticmethod
    def detect_high_variance_students(institution):
        """
        Identify students with erratic performance.
        """
        flagged = []
        students = Student.objects.filter(institution=institution)

        for student in students:
            scores = list(
                ExamResult.objects.filter(student=student).values_list('average_score', flat=True)
            )
            if len(scores) > 2:
                variance = max(scores) - min(scores)
                if variance > 30:
                    flagged.append({
                        "student_id": student.id,
                        "name": student.full_name,
                        "score_range": (min(scores), max(scores)),
                        "note": "High score variance"
                    })

        return flagged

    @staticmethod
    def identify_teacher_workload(institution):
        """
        Show teacher exam load per subject.
        """
        data = ExamSubject.objects.filter(
            exam__institution=institution
        ).values('subject__name').annotate(count=Count('id')).order_by('-count')

        return [{"subject": d['subject__name'], "exam_count": d['count']} for d in data]

    @staticmethod
    def generate_insight_summary(exam):
        """
        Generate a summary of subject-level performance.
        """
        scores = StudentScore.objects.filter(exam_subject__exam=exam)
        insights = defaultdict(lambda: {"total": 0, "high": 0, "low": 100, "grades": defaultdict(int)})

        for score in scores:
            subject = score.exam_subject.subject.name
            insights[subject]["total"] += score.score
            insights[subject]["high"] = max(insights[subject]["high"], score.score)
            insights[subject]["low"] = min(insights[subject]["low"], score.score)
            insights[subject]["grades"][score.grade] += 1

        summaries = []
        for subject, data in insights.items():
            avg = data["total"] / sum(data["grades"].values()) if data["grades"] else 0
            common_grade = max(data["grades"], key=data["grades"].get)
            summaries.append(
                f"{subject}: Avg={round(avg, 2)}, High={data['high']}, Low={data['low']}, Most Grade={common_grade}"
            )

        return "\n".join(summaries)

    @staticmethod
    def recommend_improvement_resources(subject):
        """
        Suggest revision strategies.
        """
        return [
            f"Review key concepts in {subject.name}",
            "Attempt past papers with time limits",
            "Address weak topics with teacher guidance",
            "Participate in peer learning or group study"
        ]
