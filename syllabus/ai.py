from .models import SyllabusTopic, TeachingResource, SyllabusProgress, CurriculumSubject, LearningOutcome
from django.db.models import Q, Count, Avg
from datetime import timedelta
from django.utils import timezone
import random

class SyllabusAI:
    """
    AI utility class for generating suggestions and insights for syllabus topics.
    """

    @staticmethod
    def suggest_related_topics(topic_title, subject_id):
        """
        Suggest other topics with similar keywords from the same subject.
        """
        keywords = topic_title.lower().split()
        query = Q()
        for word in keywords:
            query |= Q(title__icontains=word)
        suggestions = SyllabusTopic.objects.filter(
            query,
            curriculum_subject__subject__id=subject_id
        ).exclude(title=topic_title).distinct()[:10]
        return suggestions

    @staticmethod
    def recommend_resources_for_topic(topic_id):
        """
        Suggest existing resources for a topic based on subtopic/outcome similarity.
        """
        topic = SyllabusTopic.objects.get(id=topic_id)
        keywords = [sub.title.lower() for sub in topic.subtopics.all()]
        keywords += [out.description.lower() for out in topic.outcomes.all()]

        query = Q()
        for word in keywords:
            query |= Q(title__icontains=word) | Q(url__icontains=word)

        resources = TeachingResource.objects.filter(query).distinct()[:10]
        return resources

    @staticmethod
    def predict_coverage_progress(teacher_id):
        """
        Estimate syllabus completion rate for a given teacher.
        """
        all_progress = SyllabusProgress.objects.filter(teacher__id=teacher_id)
        total = all_progress.count()
        if total == 0:
            return 0
        covered = all_progress.filter(status='covered').count()
        return round((covered / total) * 100, 2)

    @staticmethod
    def flag_slow_topics(threshold_days=21):
        """
        Flag topics not covered X days after topic start based on estimated duration.
        """
        flags = []
        cutoff_date = timezone.now().date() - timedelta(days=threshold_days)
        pending = SyllabusProgress.objects.filter(status='pending')
        for progress in pending:
            est_date = progress.coverage_date or progress.topic.curriculum_subject.term.start_date
            if est_date and est_date < cutoff_date:
                flags.append(progress)
        return flags

    @staticmethod
    def topic_difficulty_heatmap(subject_id):
        """
        Return heatmap of topic difficulty by average time to cover vs. expected.
        """
        data = SyllabusTopic.objects.filter(
            curriculum_subject__subject__id=subject_id
        ).annotate(
            actual_coverage=Avg('syllabusprogress__coverage_date'),
            expected_minutes=Avg('estimated_duration_minutes')
        ).values('title', 'estimated_duration_minutes')[:20]
        return data

    @staticmethod
    def generate_weekly_plan(subject_id, class_level_id):
        """
        Recommend 5 topics to cover this week for a subject + level.
        """
        topics = SyllabusTopic.objects.filter(
            curriculum_subject__subject__id=subject_id,
            curriculum_subject__class_level__id=class_level_id
        ).order_by('order').exclude(
            id__in=SyllabusProgress.objects.filter(status='covered').values_list('topic_id', flat=True)
        )[:5]
        return topics
