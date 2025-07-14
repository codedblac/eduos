from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from teachers.models import Teacher
from notifications.utils import send_notification_to_user
from teachers.tasks import run_teacher_ai_analysis

User = get_user_model()


@receiver(post_save, sender=Teacher)
def create_teacher_profile(sender, instance, created, **kwargs):
    """
    On Teacher creation:
    - Send welcome notification
    - Trigger AI analysis
    """
    if created:
        # ✅ Send notification to the teacher
        if instance.user:
            send_notification_to_user(
                user=instance.user,
                title="Welcome to EduOS!",
                message=(
                    f"Your teaching profile at {instance.institution.name} has been created. "
                    "You can now access your subjects, classes, and teaching tools."
                )
            )

        # ✅ Trigger background AI task
        run_teacher_ai_analysis.delay(instance.institution.id)


@receiver(pre_save, sender=Teacher)
def log_teacher_updates(sender, instance, **kwargs):
    """
    Placeholder for future logging.
    Currently compares old vs new fields (for future use).
    """
    if not instance.pk:
        return  # Skip if creating

    try:
        old_instance = Teacher.objects.get(pk=instance.pk)
        changes = []

        for field in instance._meta.fields:
            field_name = field.name
            old_value = getattr(old_instance, field_name)
            new_value = getattr(instance, field_name)

            if field.get_internal_type() == "DateTimeField":
                if old_value and new_value and abs((old_value - new_value).total_seconds()) < 1:
                    continue

            if old_value != new_value:
                changes.append((field_name, old_value, new_value))

        # 🚧 Logging disabled for now, but comparison works and can be reused later

    except Teacher.DoesNotExist:
        pass  # Should not occur in normal usage
