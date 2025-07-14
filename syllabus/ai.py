from .models import (
    SyllabusTopic, TeachingResource, SyllabusProgress,
    CurriculumSubject, LearningOutcome
)
from django.db.models import Q, Avg
from datetime import timedelta
from django.utils import timezone
import random


class SyllabusAI:
    """
    AI utility class for generating syllabus insights and suggestions.
    """

    @staticmethod
    def suggest_related_topics(topic_title: str, subject_id: int):
        """
        Suggest topics with similar keywords in the same subject.
        """
        keywords = topic_title.lower().split()
        query = Q()
        for word in keywords:
            query |= Q(title__icontains=word)

        return SyllabusTopic.objects.filter(
            query,
            curriculum_subject__subject_id=subject_id
        ).exclude(title__iexact=topic_title).distinct()[:10]

    @staticmethod
    def recommend_resources_for_topic(topic_id: int):
        """
        Suggest learning resources based on topic subtopics/outcomes.
        """
        try:
            topic = SyllabusTopic.objects.get(id=topic_id)
        except SyllabusTopic.DoesNotExist:
            return []

        keywords = list(
            set(
                [sub.title.lower() for sub in topic.subtopics.all()] +
                [out.description.lower() for out in topic.outcomes.all()]
            )
        )

        query = Q()
        for word in keywords:
            query |= Q(title__icontains=word) | Q(url__icontains=word)

        return TeachingResource.objects.filter(query).distinct()[:10]

    @staticmethod
    def predict_coverage_progress(teacher_id: int) -> float:
        """
        Calculate % of topics marked as 'covered' by teacher.
        """
        all_progress = SyllabusProgress.objects.filter(teacher_id=teacher_id)
        total = all_progress.count()
        if total == 0:
            return 0.0
        covered = all_progress.filter(status='covered').count()
        return round((covered / total) * 100, 2)

    @staticmethod
    def flag_slow_topics(threshold_days: int = 21):
        """
        Find pending topics that are overdue.
        """
        flags = []
        cutoff = timezone.now().date() - timedelta(days=threshold_days)
        pending = SyllabusProgress.objects.filter(status='pending')

        for progress in pending:
            start_date = getattr(
                progress.topic.curriculum_subject.term, 'start_date', None
            )
            if start_date and start_date < cutoff:
                flags.append(progress)

        return flags

    @staticmethod
    def topic_difficulty_heatmap(subject_id: int):
        """
        Returns basic difficulty indicators: estimated time and progress data.
        """
        return SyllabusTopic.objects.filter(
            curriculum_subject__subject_id=subject_id
        ).annotate(
            expected_minutes=Avg('estimated_duration_minutes'),
            total_coverage=Avg('syllabusprogress__coverage_date')
        ).values('title', 'expected_minutes', 'total_coverage')[:20]

    @staticmethod
    def generate_weekly_plan(subject_id: int, class_level_id: int):
        """
        Suggest top 5 priority topics to cover this week.
        """
        covered_ids = SyllabusProgress.objects.filter(
            status='covered'
        ).values_list('topic_id', flat=True)

        return SyllabusTopic.objects.filter(
            curriculum_subject__subject_id=subject_id,
            curriculum_subject__class_level_id=class_level_id
        ).exclude(id__in=covered_ids).order_by('order')[:5]
