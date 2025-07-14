from django.db.models import Count, Avg, Max, Min, Q, F
from .models import Subject, SubjectTeacher, SubjectClassLevel
from exams.models import ExamResult
from syllabus.models import SyllabusTopic, SyllabusProgress
from institutions.models import Institution


class SubjectAnalytics:
    """
    Subject-level analytics engine for advanced insights across institutions.
    """

    @staticmethod
    def subject_performance_summary(subject_id):
        """
        Returns overall performance metrics for a subject.
        """
        results = ExamResult.objects.filter(subject_id=subject_id)
        return results.aggregate(
            average_score=Avg('marks'),
            highest_score=Max('marks'),
            lowest_score=Min('marks'),
            exam_count=Count('id')
        )

    @staticmethod
    def subject_enrollment_count(subject_id):
        """
        Unique students enrolled in a subject (based on exams).
        """
        return ExamResult.objects.filter(
            subject_id=subject_id
        ).values('student').distinct().count()

    @staticmethod
    def subjects_per_teacher(teacher_id):
        """
        List of subjects a teacher handles.
        """
        return SubjectTeacher.objects.filter(
            teacher_id=teacher_id
        ).select_related('subject').values(
            subject_id=F('subject__id'),
            subject_name=F('subject__name'),
            subject_code=F('subject__code'),
            curriculum_type=F('subject__curriculum_type')
        )

    @staticmethod
    def teacher_engagement_metrics(institution_id):
        """
        Number of teachers per subject.
        """
        return Subject.objects.filter(
            institution_id=institution_id,
            is_active=True
        ).annotate(
            total_teachers=Count('teacher_links')
        ).values(
            'id', 'name', 'code', 'curriculum_type', 'total_teachers'
        ).order_by('-total_teachers')

    @staticmethod
    def institution_subject_coverage(institution_id):
        """
        Syllabus coverage percentage per subject in institution.
        """
        subjects = Subject.objects.filter(institution_id=institution_id, is_active=True)
        data = []

        for subject in subjects:
            topic_ids = SyllabusTopic.objects.filter(
                curriculum_subject__subject=subject
            ).values_list('id', flat=True)

            progress = SyllabusProgress.objects.filter(topic_id__in=topic_ids)
            total = progress.count()
            covered = progress.filter(status='covered').count()
            coverage_percent = round((covered / total) * 100, 2) if total else 0.0

            data.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "total_topics": total,
                "covered_topics": covered,
                "coverage_percent": coverage_percent
            })

        return sorted(data, key=lambda x: x["coverage_percent"], reverse=True)

    @staticmethod
    def subject_class_distribution(subject_id):
        """
        List of class levels where a subject is taught.
        """
        return SubjectClassLevel.objects.filter(
            subject_id=subject_id
        ).select_related('class_level').values_list(
            'class_level__name', flat=True
        )

    @staticmethod
    def most_popular_subjects(institution_id, limit=10):
        """
        Subjects with highest student enrollment.
        """
        return ExamResult.objects.filter(
            student__institution_id=institution_id
        ).values(
            subject_id=F('subject__id'),
            subject_name=F('subject__name')
        ).annotate(
            student_count=Count('student', distinct=True)
        ).order_by('-student_count')[:limit]

    @staticmethod
    def lowest_performing_subjects(institution_id, limit=10):
        """
        Subjects with lowest average scores.
        """
        return ExamResult.objects.filter(
            student__institution_id=institution_id
        ).values(
            subject_id=F('subject__id'),
            subject_name=F('subject__name')
        ).annotate(
            avg_score=Avg('marks'),
            exam_count=Count('id')
        ).filter(
            exam_count__gte=5
        ).order_by('avg_score')[:limit]

    @staticmethod
    def teacher_subject_load_distribution(institution_id):
        """
        Subject count per teacher to identify workload distribution.
        """
        return SubjectTeacher.objects.filter(
            subject__institution_id=institution_id
        ).values(
            teacher_id=F('teacher__id'),
            teacher_name=F('teacher__user__full_name')
        ).annotate(
            subject_count=Count('subject', distinct=True)
        ).order_by('-subject_count')
