from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import ClassLevel, Stream
from notifications.utils import send_notification_to_user
from institutions.models import Institution
from .tasks import generate_class_insights
import uuid


@receiver(pre_save, sender=Stream)
def auto_generate_stream_code(sender, instance, **kwargs):
    """
    Auto-generate a unique stream code if not provided.
    """
    if not instance.code:
        base = instance.name.replace(" ", "").upper()
        suffix = uuid.uuid4().hex[:4].upper()
        instance.code = f"{base}-{suffix}"


@receiver(post_save, sender=ClassLevel)
def notify_class_level_created(sender, instance, created, **kwargs):
    """
    Notify institution admins when a new ClassLevel is created.
    """
    if created:
        institution = instance.institution
        admins = institution.customuser_set.filter(is_staff=True)
        for admin in admins:
            send_notification_to_user(
                user=admin,
                title="New Class Level Created",
                message=f"A new class level '{instance.name}' has been created for {institution.name}."
            )


@receiver(post_save, sender=Stream)
def handle_stream_post_save(sender, instance, created, **kwargs):
    """
    Handles both notifications and AI generation when a Stream is created or updated.
    """
    institution = instance.institution
    class_level = instance.class_level
    admins = institution.customuser_set.filter(is_staff=True)

    if created:
        for admin in admins:
            send_notification_to_user(
                user=admin,
                title="New Stream Created",
                message=f"A new stream '{instance.name}' has been added to class level '{class_level.name}' in {institution.name}."
            )

    # Trigger async AI insight generation task
    generate_class_insights.delay(institution_id=str(institution.id))
