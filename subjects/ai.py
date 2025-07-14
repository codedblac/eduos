from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q, F

from .models import Subject, SubjectTeacher
from exams.models import ExamResult
from syllabus.models import SyllabusTopic, SyllabusProgress


class SubjectAIEngine:
    """
    AI engine for intelligent analytics, diagnostics, and decision support
    across subjects in the EduOS system.
    """

    @staticmethod
    def recommend_difficult_subjects_by_performance(institution_id, min_enrollments=10):
        """
        Identify subjects with low average scores and meaningful data points.
        """
        return ExamResult.objects.filter(
            student__institution_id=institution_id
        ).values(
            subject_id=F('subject__id'),
            subject_name=F('subject__name')
        ).annotate(
            avg_score=Avg('marks'),
            student_count=Count('student', distinct=True)
        ).filter(
            student_count__gte=min_enrollments
        ).order_by('avg_score')[:10]

    @staticmethod
    def predict_teacher_load(teacher_id):
        """
        Estimate workload for a teacher based on assigned subjects and topic volume.
        """
        subject_ids = SubjectTeacher.objects.filter(
            teacher_id=teacher_id
        ).values_list('subject_id', flat=True)

        total_subjects = len(subject_ids)
        topic_count = SyllabusTopic.objects.filter(
            curriculum_subject__subject_id__in=subject_ids
        ).count()

        return {
            "teacher_id": teacher_id,
            "assigned_subjects": total_subjects,
            "estimated_topics_to_cover": topic_count,
            "teaching_load_score": round(topic_count / max(total_subjects, 1), 2)
        }

    @staticmethod
    def get_subject_popularity(institution_id, top_n=10):
        """
        Get most popular subjects based on student enrollment.
        """
        return ExamResult.objects.filter(
            student__institution_id=institution_id
        ).values(
            subject_id=F('subject__id'),
            subject_name=F('subject__name')
        ).annotate(
            student_count=Count('student', distinct=True)
        ).order_by('-student_count')[:top_n]

    @staticmethod
    def detect_subjects_with_coverage_gaps(institution_id, threshold=60.0):
        """
        Detect subjects with coverage below threshold.
        """
        return SyllabusProgress.objects.filter(
            topic__curriculum_subject__curriculum__institution_id=institution_id
        ).values(
            subject_id=F('topic__curriculum_subject__subject__id'),
            subject_name=F('topic__curriculum_subject__subject__name')
        ).annotate(
            total=Count('id'),
            covered=Count('id', filter=Q(status='covered'))
        ).annotate(
            coverage_percent=100.0 * F('covered') / F('total')
        ).filter(
            coverage_percent__lt=threshold
        ).order_by('coverage_percent')

    @staticmethod
    def pacing_recommendation(subject_id, class_level_id, term_weeks=12):
        """
        Recommend pacing plan based on topic count and term duration.
        """
        topics = SyllabusTopic.objects.filter(
            curriculum_subject__subject_id=subject_id,
            curriculum_subject__class_level_id=class_level_id
        )
        total_topics = topics.count()
        topics_per_week = total_topics / term_weeks if total_topics else 0

        return {
            "subject_id": subject_id,
            "class_level_id": class_level_id,
            "total_topics": total_topics,
            "recommended_topics_per_week": round(topics_per_week, 2)
        }

    @staticmethod
    def flag_subjects_without_teachers(institution_id):
        """
        Find active subjects with no assigned teachers.
        """
        return Subject.objects.filter(
            institution_id=institution_id,
            is_active=True
        ).annotate(
            teacher_count=Count('teacher_links')
        ).filter(
            teacher_count=0
        ).values('id', 'name')

    @staticmethod
    def recommend_teachers_for_subject(subject_id):
        """
        Suggest teachers who taught the subject previously.
        """
        history = SubjectTeacher.objects.filter(
            subject_id=subject_id
        ).select_related('teacher__user').distinct()

        return [
            {
                "teacher_id": t.teacher.id,
                "teacher_name": t.teacher.user.get_full_name() if t.teacher and t.teacher.user else "N/A",
                "last_assigned": t.assigned_at
            }
            for t in history.order_by('-assigned_at')[:5]
        ]

    @staticmethod
    def subject_summary(subject_id):
        """
        Return performance, staffing, and coverage summary for a subject.
        """
        avg_score = ExamResult.objects.filter(
            subject_id=subject_id
        ).aggregate(avg=Avg('marks'))['avg'] or 0

        student_count = ExamResult.objects.filter(
            subject_id=subject_id
        ).values('student').distinct().count()

        teacher_count = SubjectTeacher.objects.filter(
            subject_id=subject_id
        ).count()

        topic_total = SyllabusTopic.objects.filter(
            curriculum_subject__subject_id=subject_id
        ).count()

        topic_covered = SyllabusProgress.objects.filter(
            topic__curriculum_subject__subject_id=subject_id,
            status='covered'
        ).count()

        coverage_percent = (topic_covered / topic_total * 100) if topic_total else 0

        return {
            "subject_id": subject_id,
            "average_score": round(avg_score, 2),
            "student_enrollment": student_count,
            "teachers_assigned": teacher_count,
            "syllabus_topics": topic_total,
            "topics_covered": topic_covered,
            "syllabus_coverage_percent": round(coverage_percent, 1)
        }
