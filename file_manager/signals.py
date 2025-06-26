from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import ManagedFile, FileVersion, FileAccessLog, FileAnalytics
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ManagedFile)
def create_file_analytics(sender, instance, created, **kwargs):
    """
    Automatically create an analytics record for each new uploaded file.
    """
    if created:
        FileAnalytics.objects.create(file=instance)
        logger.info(f"Analytics created for new file: {instance.name} (ID: {instance.id})")


@receiver(post_save, sender=FileAccessLog)
def update_file_analytics(sender, instance, created, **kwargs):
    """
    Update view/download counters and last accessed time.
    """
    if created:
        try:
            analytics, _ = FileAnalytics.objects.get_or_create(file=instance.file)
            if instance.action == "viewed":
                analytics.view_count += 1
            elif instance.action == "downloaded":
                analytics.download_count += 1
            analytics.last_accessed = instance.accessed_at
            analytics.save()
            logger.info(f"Analytics updated for file: {instance.file.name} (Action: {instance.action})")
        except Exception as e:
            logger.error(f"Error updating analytics for file {instance.file_id}: {e}")


@receiver(post_save, sender=FileVersion)
def log_file_version(sender, instance, created, **kwargs):
    """
    Log or trigger notifications when a new file version is uploaded.
    """
    if created:
        logger.info(f"New version uploaded: {instance.managed_file.name} v{instance.version_number}")
        # Future: trigger notification task or audit log entry here
