from celery import shared_task
from django.utils import timezone
from django.db.models import Avg
from .models import Subject, SubjectTeacher, SubjectAnalyticsLog
from exams.models import ExamResult
from syllabus.models import SyllabusProgress
from accounts.models import CustomUser
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_subject_performance_trends():
    """
    Calculate average performance for each subject and log analytics.
    """
    subjects = Subject.objects.filter(is_active=True)

    for subject in subjects:
        exam_results = ExamResult.objects.filter(subject=subject)

        if not exam_results.exists():
            continue

        avg_score = exam_results.aggregate(avg=Avg('marks'))['avg'] or 0.0
        highest = exam_results.order_by('-marks').first().marks if exam_results.exists() else 0.0
        lowest = exam_results.order_by('marks').first().marks if exam_results.exists() else 0.0

        SubjectAnalyticsLog.objects.create(
            subject=subject,
            average_score=avg_score,
            highest_score=highest,
            lowest_score=lowest,
            recorded_at=timezone.now()
        )

        logger.info(f"[Analytics] Logged performance for subject: {subject.name}")


@shared_task
def notify_subject_heads_on_coverage_gaps(threshold_percentage=50):
    """
    Notify subject heads if syllabus coverage is below a given threshold.
    """
    subjects = Subject.objects.filter(is_active=True)

    for subject in subjects:
        total_topics = subject.syllabustopic_set.count()
        if total_topics == 0:
            continue

        covered = SyllabusProgress.objects.filter(
            topic__curriculum_subject__subject=subject,
            status='covered'
        ).count()

        coverage_percent = (covered / total_topics) * 100

        if coverage_percent < threshold_percentage:
            heads = subject.teacher_links.filter(is_head=True).select_related('teacher__user')
            for link in heads:
                user = getattr(link.teacher, 'user', None)
                if user and user.email:
                    # Replace with notification system
                    logger.warning(
                        f"[Coverage Alert] Subject '{subject.name}' is only {coverage_percent:.2f}% covered. Alert sent to {user.email}"
                    )


@shared_task
def sync_teacher_subject_assignments():
    """
    Ensure core subjects have at least one teacher assigned.
    """
    subjects = Subject.objects.filter(is_core=True, is_active=True)

    for subject in subjects:
        if subject.teacher_links.exists():
            continue

        institution = subject.institution
        fallback_users = CustomUser.objects.filter(
            institution=institution,
            is_staff=True,
            role='teacher'
        ).select_related('teacher_profile')[:1]

        for user in fallback_users:
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                SubjectTeacher.objects.create(subject=subject, teacher=teacher, is_head=True)
                logger.info(f"[Auto Assign] Core subject '{subject.name}' assigned to {user.get_full_name()}")
            else:
                logger.warning(f"[Auto Assign Failed] No teacher profile for user {user}")


@shared_task
def archive_deprecated_subjects():
    """
    Archive subjects that are not assigned to any class level or topics.
    """
    subjects = Subject.objects.filter(is_active=True)

    for subject in subjects:
        has_class_links = subject.class_levels.exists()
        has_topics = subject.syllabustopic_set.exists()

        if not has_class_links and not has_topics:
            subject.is_active = False
            subject.archived = True
            subject.save(update_fields=['is_active', 'archived'])
            logger.info(f"[Archive] Subject '{subject.name}' archived due to no usage.")
