# accounts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from accounts.tasks import (
    send_welcome_email_task,
    log_user_action_task
)


@receiver(post_save, sender=CustomUser)
def handle_user_creation(sender, instance, created, **kwargs):
    """
    Trigger tasks after a new user is created.
    """
    if created:
        # Send welcome email
        send_welcome_email_task.delay(instance.id)

        # Log creation event
        log_user_action_task.delay(
            user_id=instance.id,
            action="account_created",
            metadata={"role": instance.role, "institution_id": instance.institution_id}
        )
    else:
        # Optionally log profile update events
        log_user_action_task.delay(
            user_id=instance.id,
            action="account_updated",
            metadata={"institution_id": instance.institution_id}
        )
