from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    SyllabusTopic, SyllabusSubtopic, LearningOutcome,
    SyllabusProgress, SyllabusAuditLog
)


@receiver(post_save, sender=SyllabusTopic)
def log_topic_created(sender, instance, created, **kwargs):
    if created:
        SyllabusAuditLog.objects.create(
            user=getattr(instance, 'created_by', None),
            action='Created Topic',
            curriculum_subject=instance.curriculum_subject,
            topic=instance,
            notes=f"Topic '{instance.title}' was created."
        )


@receiver(post_save, sender=SyllabusProgress)
def log_progress_update(sender, instance, created, **kwargs):
    # Prevent duplicate logs on initial creation unless it’s meaningful
    if created and instance.status == 'pending':
        return

    action = {
        'covered': 'Marked as Covered',
        'skipped': 'Marked as Skipped',
        'pending': 'Progress Updated'
    }.get(instance.status, 'Progress Updated')

    SyllabusAuditLog.objects.create(
        user=instance.teacher,
        action=action,
        curriculum_subject=instance.topic.curriculum_subject,
        topic=instance.topic,
        notes=f"Status set to '{instance.status}' on {timezone.now().date()}."
    )


@receiver(post_delete, sender=SyllabusTopic)
def log_topic_deleted(sender, instance, **kwargs):
    SyllabusAuditLog.objects.create(
        user=getattr(instance, 'created_by', None),
        action='Deleted Topic',
        curriculum_subject=instance.curriculum_subject,
        topic=None,
        notes=f"Topic '{instance.title}' was deleted."
    )
