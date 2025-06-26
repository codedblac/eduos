from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import AlumniProfile, AlumniContribution
from notifications.utils import send_notification_to_admins


@receiver(post_save, sender=AlumniContribution)
def handle_contribution_post_save(sender, instance, created, **kwargs):
    if created:
        alumni = instance.alumni
        alumni.engagement_score += 0.1  # boost score
        alumni.last_active = timezone.now()
        alumni.save()

        # Send a notification if contribution is large
        if instance.amount >= 10000:  # adjust threshold as needed
            send_notification_to_admins(
                institution=instance.institution,
                title="🎉 Major Alumni Contribution",
                message=f"{alumni.user.get_full_name()} just contributed KES {instance.amount:,}!"
            )


@receiver(post_save, sender=AlumniProfile)
def update_alumni_activity(sender, instance, created, **kwargs):
    if not created:
        instance.last_active = timezone.now()
        instance.save()
