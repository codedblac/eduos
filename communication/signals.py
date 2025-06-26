from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import CommunicationAnnouncement, CommunicationLog
from .tasks import send_announcement_now
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CommunicationAnnouncement)
def handle_announcement_post_save(sender, instance, created, **kwargs):
    if created:
        CommunicationLog.objects.create(
            announcement=instance,
            status="created",
            details="Announcement created"
        )

        # Trigger send immediately if not scheduled and not already sent
        if not instance.scheduled_at and not instance.sent:
            logger.info(f"Sending announcement {instance.title} immediately.")
            send_announcement_now.delay(instance.id)
        else:
            logger.info(f"Announcement {instance.title} scheduled for {instance.scheduled_at}.")
    else:
        CommunicationLog.objects.create(
            announcement=instance,
            status="updated",
            details="Announcement updated"
        )


@receiver(pre_delete, sender=CommunicationAnnouncement)
def handle_announcement_pre_delete(sender, instance, **kwargs):
    CommunicationLog.objects.create(
        announcement=instance,
        status="deleted",
        details="Announcement deleted"
    )
