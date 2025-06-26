from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    SyllabusTopic, SyllabusSubtopic, LearningOutcome,
    SyllabusProgress, SyllabusAuditLog
)
from django.utils import timezone


@receiver(post_save, sender=SyllabusTopic)
def log_topic_created(sender, instance, created, **kwargs):
    if created:
        SyllabusAuditLog.objects.create(
            user=None,  # Filled later via admin or view context
            action='Created Topic',
            curriculum_subject=instance.curriculum_subject,
            topic=instance,
            notes=f"Topic '{instance.title}' created."
        )


@receiver(post_save, sender=SyllabusProgress)
def log_progress_update(sender, instance, created, **kwargs):
    action = 'Marked as Covered' if instance.status == 'covered' else 'Progress Updated'
    SyllabusAuditLog.objects.create(
        user=instance.teacher,
        action=action,
        curriculum_subject=instance.topic.curriculum_subject,
        topic=instance.topic,
        notes=f"Status: {instance.status}, Date: {instance.coverage_date}"
    )


@receiver(post_delete, sender=SyllabusTopic)
def log_topic_deleted(sender, instance, **kwargs):
    SyllabusAuditLog.objects.create(
        user=None,
        action='Deleted Topic',
        curriculum_subject=instance.curriculum_subject,
        topic=None,
        notes=f"Topic '{instance.title}' was deleted."
    )
