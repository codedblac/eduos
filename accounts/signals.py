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
    Trigger background actions after user creation/update.
    """
    try:
        # Primary role is a string now
        primary_role_name = instance.primary_role

        # Get assigned modules names
        assigned_modules = list(instance.modules.values_list("name", flat=True))

        metadata = {
            "institution_id": instance.institution_id,
            "primary_role": primary_role_name,
            "assigned_modules": assigned_modules,
        }

        if created:
            # 🚀 Send welcome email asynchronously
            send_welcome_email_task.delay(instance.id)

            # 📝 Log account creation
            log_user_action_task.delay(
                user_id=instance.id,
                action="account_created",
                metadata=metadata
            )
        else:
            # 📝 Log account update
            log_user_action_task.delay(
                user_id=instance.id,
                action="account_updated",
                metadata=metadata
            )

    except Exception as e:
        # Prevent signal failure from blocking user save
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(f"Error processing post_save signal for CustomUser: {e}")
