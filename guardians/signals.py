from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GuardianNotification, GuardianStudentLink
from .tasks import send_guardian_notification_email
from django.utils.timezone import now


@receiver(post_save, sender=GuardianNotification)
def handle_guardian_notification_created(sender, instance, created, **kwargs):
    """
    Trigger email sending when a new GuardianNotification is created.
    """
    if created:
        send_guardian_notification_email.delay(instance.id)


@receiver(post_save, sender=GuardianStudentLink)
def auto_notify_on_linking(sender, instance, created, **kwargs):
    """
    Notify guardian when a student is linked to them.
    """
    if created:
        message = f"You have been linked to student {instance.student.full_name} as their {instance.get_relationship_display()}."
        GuardianNotification.objects.create(
            guardian=instance.guardian,
            institution=instance.guardian.institution,
            title="New Student Link",
            message=message,
            type="announcement",
            timestamp=now()
        )
