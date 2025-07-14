from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging

from .models import Subject, SubjectTeacher, SubjectClassLevel
from syllabus.models import CurriculumSubject
from teachers.models import Teacher

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Subject)
def create_subject_audit_log(sender, instance, created, **kwargs):
    """
    Log creation or update of a subject.
    """
    action = "Created" if created else "Updated"
    logger.info(f"[SubjectAudit] {action} subject '{instance.name}' at {timezone.now()}")


@receiver(post_delete, sender=Subject)
def delete_subject_log(sender, instance, **kwargs):
    logger.info(f"[SubjectAudit] Deleted subject '{instance.name}' at {timezone.now()}")


@receiver(post_save, sender=SubjectTeacher)
def auto_assign_teacher_subjects(sender, instance, created, **kwargs):
    """
    Log assignment of a teacher to a subject.
    """
    if created:
        teacher_name = (
            instance.teacher.user.get_full_name()
            if instance.teacher and instance.teacher.user else str(instance.teacher)
        )
        logger.info(
            f"[TeacherLink] Linked teacher '{teacher_name}' to subject '{instance.subject.name}' at {timezone.now()}"
        )


@receiver(post_delete, sender=SubjectTeacher)
def unlink_teacher_subject_log(sender, instance, **kwargs):
    """
    Log unassignment of a teacher from a subject.
    """
    teacher_name = (
        instance.teacher.user.get_full_name()
        if instance.teacher and instance.teacher.user else str(instance.teacher)
    )
    logger.info(
        f"[TeacherLink] Unlinked teacher '{teacher_name}' from subject '{instance.subject.name}' at {timezone.now()}"
    )


@receiver(post_save, sender=SubjectClassLevel)
def ensure_curriculum_subject_link(sender, instance, created, **kwargs):
    """
    Auto-create CurriculumSubject entries for each term when subject is added to a class level.
    """
    if not created:
        return

    try:
        from academics.models import Term

        subject = instance.subject
        institution = subject.institution
        curriculum = getattr(institution, 'default_curriculum', None)

        if not curriculum:
            logger.warning(
                f"[CurriculumSync] No default curriculum set for institution '{institution.name}'. Skipping link."
            )
            return

        terms = Term.objects.all()
        created_terms = []

        for term in terms:
            obj, was_created = CurriculumSubject.objects.get_or_create(
                curriculum=curriculum,
                subject=subject,
                class_level=instance.class_level,
                term=term,
                defaults={'ordering': 0}
            )
            if was_created:
                created_terms.append(term.name)

        if created_terms:
            logger.info(
                f"[CurriculumSync] Linked subject '{subject.name}' to curriculum for terms: {', '.join(created_terms)}"
            )

    except Exception as e:
        logger.exception(
            f"[CurriculumSyncError] Failed to link subject '{instance.subject.name}' to curriculum: {str(e)}"
        )
