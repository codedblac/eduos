from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Institution, SchoolAccount
from .tasks import send_institution_welcome_email
import logging

logger = logging.getLogger(__name__)

# =============================
# 🏫 Institution Signals
# =============================

@receiver(post_save, sender=Institution)
def institution_created_or_updated(sender, instance, created, **kwargs):
    """
    Triggered whenever an Institution is created or updated.
    On creation: send welcome email asynchronously.
    On update: log changes.
    """
    if created:
        logger.info(f"[Institution Created] {instance.name} ({instance.code})")
        # Trigger async welcome email or onboarding tasks
        send_institution_welcome_email.delay(instance.id)
    else:
        logger.info(f"[Institution Updated] {instance.name} ({instance.code})")

# =============================
# 💳 SchoolAccount Signals
# =============================

@receiver(post_save, sender=SchoolAccount)
def school_account_created_or_updated(sender, instance, created, **kwargs):
    """
    Triggered whenever a SchoolAccount is created or updated.
    Logs creation events; updates default account status if needed.
    """
    if created:
        logger.info(f"[Account Created] {instance.institution.name} - {instance.account_name}")
    else:
        logger.info(f"[Account Updated] {instance.institution.name} - {instance.account_name}")
