from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ELibraryResource, ResourceViewLog
from .tasks import auto_generate_summaries_and_tags
from notifications.utils import send_notification


@receiver(post_save, sender=ELibraryResource)
def handle_resource_upload(sender, instance, created, **kwargs):
    """
    When a new resource is uploaded:
    - Optionally send notification to admins for approval
    - Queue AI task for summary and tag generation
    """
    if created:
        # Notify institution admins for approval
        admins = instance.institution.users.filter(profile__role__in=["admin", "super_admin"])
        for admin in admins:
            send_notification(
                user=admin,
                title="New Resource Pending Approval",
                message=f"A new resource titled '{instance.title}' has been uploaded by {instance.uploader}.",
                target="e_library"
            )

        # Trigger AI tasks if file is attached
        if instance.file:
            auto_generate_summaries_and_tags.delay()


@receiver(post_save, sender=ResourceViewLog)
def track_resource_view(sender, instance, created, **kwargs):
    """
    Track views and optionally notify uploader (optional feature).
    """
    if created and instance.user and instance.user != instance.resource.uploader:
        # Notify uploader of engagement (optional, comment out if too noisy)
        pass
        # send_notification(
        #     user=instance.resource.uploader,
        #     title="Resource Viewed",
        #     message=f"{instance.user.username} viewed your resource: {instance.resource.title}.",
        #     target="e_library"
        # )
