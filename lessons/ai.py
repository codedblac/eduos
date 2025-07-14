from .models import LessonPlan, LessonSchedule, LessonSession
from subjects.models import Subject
from syllabus.models import SyllabusTopic, SyllabusSubtopic
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
import random


class LessonAI:
    """
    AI utilities for assisting lesson planning, scheduling, and analysis.
    """

    @staticmethod
    def suggest_lesson_template(subject_id, topic_id=None):
        """
        Suggest a lesson scaffold including summary, objectives, and suggested activities.
        """
        topic = SyllabusTopic.objects.filter(id=topic_id).first()
        subtopics = SyllabusSubtopic.objects.filter(topic=topic) if topic else []

        summary = topic.description if topic else "This lesson covers foundational concepts."
        objectives = [
            f"Understand {sub.title}" for sub in subtopics[:3]
        ] if subtopics else ["Understand the key concepts of the topic."]

        teaching_methods = random.sample(['lecture', 'discussion', 'practical', 'digital', 'hybrid'], 2)
        resources = [
            "Textbook reference",
            "Visual aids",
            "Interactive exercise",
            "Multimedia video"
        ]

        return {
            "summary": summary,
            "objectives": objectives,
            "suggested_methods": teaching_methods,
            "suggested_resources": random.sample(resources, k=3),
        }

    @staticmethod
    def detect_unplanned_weeks(teacher_id, subject_id, term_id):
        """
        Identify weeks where lesson plans are missing.
        """
        existing_weeks = LessonPlan.objects.filter(
            teacher_id=teacher_id, subject_id=subject_id, term_id=term_id
        ).values_list('week_number', flat=True)

        all_weeks = set(range(1, 14))  # assume 13-week term
        missing = sorted(list(all_weeks - set(existing_weeks)))
        return missing

    @staticmethod
    def recommend_upcoming_lessons(teacher_id, subject_id, class_level_id, term_id):
        """
        Recommend upcoming topics for lesson planning based on syllabus order.
        """
        covered_topics = LessonPlan.objects.filter(
            teacher_id=teacher_id,
            subject_id=subject_id,
            class_level_id=class_level_id,
            term_id=term_id
        ).values_list('topic_id', flat=True)

        upcoming_topics = SyllabusTopic.objects.filter(
            curriculum_subject__subject_id=subject_id,
            curriculum_subject__class_level_id=class_level_id
        ).exclude(id__in=covered_topics).order_by('order')[:5]

        return upcoming_topics

    @staticmethod
    def predict_lesson_gap_alerts(institution_id):
        """
        Detect institutions, classes or teachers with low coverage or skipped sessions.
        """
        recent_cutoff = timezone.now().date() - timedelta(days=14)

        skipped_sessions = LessonSession.objects.filter(
            lesson_schedule__lesson_plan__institution_id=institution_id,
            coverage_status__in=['skipped', 'cancelled'],
            delivered_on__gte=recent_cutoff
        ).values('lesson_schedule__lesson_plan__teacher__id').annotate(
            total=Count('id')
        ).order_by('-total')

        return skipped_sessions

    @staticmethod
    def lesson_delivery_trend(subject_id):
        """
        Return the weekly count of lessons delivered for a subject.
        """
        from django.db.models.functions import ExtractWeek

        return LessonSession.objects.filter(
            lesson_schedule__lesson_plan__subject_id=subject_id,
            coverage_status='covered'
        ).annotate(
            week=ExtractWeek('delivered_on')
        ).values('week').annotate(
            total=Count('id')
        ).order_by('week')
