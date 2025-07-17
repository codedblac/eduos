# departments/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now

from departments.models import DepartmentUser, Subject
from departments.tasks import (
    send_department_role_notification,
    compute_department_performance,
    compute_teacher_attendance,
    notify_underperforming_students
)

import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=DepartmentUser)
def handle_department_user_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal triggered when a DepartmentUser is created or updated.
    """
    try:
        if created:
            # Notify user about their role assignment
            send_department_role_notification.delay(instance.id)

        # Trigger performance and attendance recomputation
        compute_department_performance.delay(instance.department_id)
        compute_teacher_attendance.delay(instance.department_id)

    except Exception as e:
        logger.error(f"[DepartmentUser Signal] Error: {str(e)}")


@receiver(post_delete, sender=DepartmentUser)
def handle_department_user_deleted(sender, instance, **kwargs):
    """
    Signal triggered when a DepartmentUser is deleted.
    """
    try:
        compute_department_performance.delay(instance.department_id)
        compute_teacher_attendance.delay(instance.department_id)
    except Exception as e:
        logger.error(f"[DepartmentUser Delete Signal] Error: {str(e)}")


@receiver(post_save, sender=Subject)
def handle_subject_save(sender, instance, created, **kwargs):
    """
    Signal triggered when a Subject is created or updated.
    """
    try:
        compute_department_performance.delay(instance.department_id)

        # Optional: notify guardians of underperforming students
        notify_underperforming_students.delay(instance.id)

    except Exception as e:
        logger.error(f"[Subject Save Signal] Error: {str(e)}")


@receiver(post_delete, sender=Subject)
def handle_subject_delete(sender, instance, **kwargs):
    """
    Signal triggered when a Subject is deleted.
    """
    try:
        compute_department_performance.delay(instance.department_id)
    except Exception as e:
        logger.error(f"[Subject Delete Signal] Error: {str(e)}")
