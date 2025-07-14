from django.db.models import Count, Avg, Q
from .models import (
    SyllabusTopic, SyllabusProgress, CurriculumSubject, LearningOutcome
)


class SyllabusAnalytics:
    """
    Analytics engine for syllabus usage, coverage, and performance insights.
    """

    @staticmethod
    def syllabus_coverage_by_teacher(teacher_id: int) -> dict:
        """
        Return syllabus coverage breakdown for a specific teacher.
        """
        qs = SyllabusProgress.objects.filter(teacher_id=teacher_id)
        total = qs.count()
        covered = qs.filter(status='covered').count()
        skipped = qs.filter(status='skipped').count()
        pending = total - (covered + skipped)

        return {
            'teacher_id': teacher_id,
            'total_topics': total,
            'covered': covered,
            'skipped': skipped,
            'pending': pending,
            'percentage_covered': round((covered / total) * 100, 2) if total else 0.0
        }

    @staticmethod
    def coverage_by_class_level(class_level_id: int) -> dict:
        """
        Return syllabus progress summary for a specific class level.
        """
        topics = SyllabusTopic.objects.filter(curriculum_subject__class_level_id=class_level_id)
        topic_ids = topics.values_list('id', flat=True)
        progress = SyllabusProgress.objects.filter(topic_id__in=topic_ids)

        return {
            'class_level_id': class_level_id,
            'total_topics': topics.count(),
            'progress_entries': progress.count(),
            'covered': progress.filter(status='covered').count(),
            'skipped': progress.filter(status='skipped').count(),
            'pending': progress.filter(status='pending').count()
        }

    @staticmethod
    def teacher_topic_distribution(limit: int = 20) -> list:
        """
        Return top teachers by topic coverage count.
        """
        return (
            SyllabusProgress.objects.filter(status='covered')
            .values('teacher__id', 'teacher__first_name', 'teacher__last_name')
            .annotate(total_covered=Count('id'))
            .order_by('-total_covered')[:limit]
        )

    @staticmethod
    def most_skipped_topics(limit: int = 10) -> list:
        """
        List most skipped topics across the system.
        """
        return (
            SyllabusProgress.objects.filter(status='skipped')
            .values('topic__id', 'topic__title')
            .annotate(skip_count=Count('id'))
            .order_by('-skip_count')[:limit]
        )

    @staticmethod
    def outcomes_per_topic(limit: int = 20) -> list:
        """
        Return topics with most learning outcomes.
        """
        return (
            LearningOutcome.objects.values('topic__id', 'topic__title')
            .annotate(outcomes_count=Count('id'))
            .order_by('-outcomes_count')[:limit]
        )

    @staticmethod
    def institution_topic_coverage(institution_id: int) -> dict:
        """
        Return topic coverage % for a given institution.
        """
        curriculum_subjects = CurriculumSubject.objects.filter(curriculum__institution_id=institution_id)
        topics = SyllabusTopic.objects.filter(curriculum_subject__in=curriculum_subjects)
        topic_ids = topics.values_list('id', flat=True)

        progress = SyllabusProgress.objects.filter(topic_id__in=topic_ids)
        total_progress = progress.count()
        covered = progress.filter(status='covered').count()

        return {
            'institution_id': institution_id,
            'topics_total': topics.count(),
            'progress_entries': total_progress,
            'covered': covered,
            'percentage_covered': round((covered / total_progress) * 100, 2) if total_progress else 0.0
        }

    @staticmethod
    def syllabus_progress_summary() -> dict:
        """
        Global syllabus progress stats.
        """
        total = SyllabusProgress.objects.count()
        covered = SyllabusProgress.objects.filter(status='covered').count()
        skipped = SyllabusProgress.objects.filter(status='skipped').count()
        pending = total - (covered + skipped)

        return {
            'total_progress_entries': total,
            'covered': covered,
            'skipped': skipped,
            'pending': pending,
            'global_coverage_rate': round((covered / total) * 100, 2) if total else 0.0
        }
