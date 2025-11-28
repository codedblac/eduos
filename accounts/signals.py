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
        # primary_role is a string now, no need to access .name
        primary_role_name = instance.primary_role

        # Optional additional roles, if you ever implement a separate roles M2M
        additional_roles = (
            list(instance.roles.values_list("name", flat=True))
            if hasattr(instance, "roles") else []
        )

        metadata = {
            "institution_id": instance.institution_id,
            "primary_role": primary_role_name,
            "additional_roles": additional_roles,
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
                metadata={
                    "institution_id": instance.institution_id,
                    "primary_role": primary_role_name
                }
            )

    except Exception as e:
        # Prevent user creation from failing if signal tasks fail
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(f"Error processing post_save signal for CustomUser: {e}")
