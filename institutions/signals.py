from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Institution, SchoolAccount
from .tasks import send_institution_welcome_email
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Institution)
def institution_created_or_updated(sender, instance, created, **kwargs):
    if created:
        logger.info(f"[Institution Created] {instance.name} ({instance.code})")
        # Trigger async welcome email or setup
        send_institution_welcome_email.delay(instance.id)
    else:
        logger.info(f"[Institution Updated] {instance.name} ({instance.code})")


@receiver(post_save, sender=SchoolAccount)
def school_account_created(sender, instance, created, **kwargs):
    if created:
        logger.info(f"[Account Created] {instance.institution.name} - {instance.account_name}")
