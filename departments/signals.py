from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DepartmentUser, Subject
from .tasks import (
    send_department_role_notification,
    compute_department_performance,
    compute_teacher_attendance,
    notify_underperforming_students
)


@receiver(post_save, sender=DepartmentUser)
def handle_department_user_created_or_updated(sender, instance, created, **kwargs):
    # Notify user of role assignment on creation
    if created:
        send_department_role_notification.delay(instance.id)

    # Recompute department performance and attendance on any save
    compute_department_performance.delay(instance.department.id)
    compute_teacher_attendance.delay(instance.department.id)


@receiver(post_delete, sender=DepartmentUser)
def handle_department_user_deleted(sender, instance, **kwargs):
    # Recompute department performance and attendance on deletion
    compute_department_performance.delay(instance.department.id)
    compute_teacher_attendance.delay(instance.department.id)


@receiver(post_save, sender=Subject)
def handle_subject_save(sender, instance, created, **kwargs):
    # Re-evaluate performance per subject on save
    compute_department_performance.delay(instance.department.id)
    
    # Optionally notify about underperforming students
    notify_underperforming_students.delay(instance.id)


@receiver(post_delete, sender=Subject)
def handle_subject_delete(sender, instance, **kwargs):
    # Recalculate department metrics after subject deletion
    compute_department_performance.delay(instance.department.id)
