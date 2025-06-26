from django.db.models import Count, Avg, Q
from .models import SyllabusTopic, SyllabusProgress, CurriculumSubject, LearningOutcome

class SyllabusAnalytics:
    """
    Analytics engine for syllabus usage, coverage, and performance insights.
    """

    @staticmethod
    def syllabus_coverage_by_teacher(teacher_id):
        total = SyllabusProgress.objects.filter(teacher_id=teacher_id).count()
        covered = SyllabusProgress.objects.filter(teacher_id=teacher_id, status='covered').count()
        skipped = SyllabusProgress.objects.filter(teacher_id=teacher_id, status='skipped').count()
        pending = total - (covered + skipped)

        return {
            'total': total,
            'covered': covered,
            'skipped': skipped,
            'pending': pending,
            'percentage_covered': round((covered / total * 100), 2) if total else 0,
        }

    @staticmethod
    def coverage_by_class_level(class_level_id):
        topics = SyllabusTopic.objects.filter(curriculum_subject__class_level_id=class_level_id)
        topic_ids = topics.values_list('id', flat=True)
        progress = SyllabusProgress.objects.filter(topic_id__in=topic_ids)

        return {
            'class_level': class_level_id,
            'topics_total': topics.count(),
            'progress_entries': progress.count(),
            'covered': progress.filter(status='covered').count(),
            'skipped': progress.filter(status='skipped').count(),
        }

    @staticmethod
    def teacher_topic_distribution():
        """
        Distribution of how many topics each teacher has covered.
        """
        return SyllabusProgress.objects.filter(status='covered').values('teacher__id', 'teacher__first_name', 'teacher__last_name').annotate(
            total=Count('id')
        ).order_by('-total')

    @staticmethod
    def most_skipped_topics(limit=10):
        """
        Topics skipped most often across the platform.
        """
        return SyllabusProgress.objects.filter(status='skipped').values('topic__title').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

    @staticmethod
    def outcomes_per_topic():
        """
        Counts learning outcomes per topic.
        """
        return LearningOutcome.objects.values('topic__title').annotate(
            outcomes_count=Count('id')
        ).order_by('-outcomes_count')[:20]

    @staticmethod
    def institution_topic_coverage(institution_id):
        """
        Returns overall topic coverage percentage for a given institution.
        """
        curriculum_subjects = CurriculumSubject.objects.filter(curriculum__institution_id=institution_id)
        topics = SyllabusTopic.objects.filter(curriculum_subject__in=curriculum_subjects)
        progress = SyllabusProgress.objects.filter(topic__in=topics)
        total = progress.count()
        covered = progress.filter(status='covered').count()

        return {
            'institution': institution_id,
            'topics_counted': topics.count(),
            'progress_total': total,
            'percentage_covered': round((covered / total) * 100, 2) if total else 0,
        }
