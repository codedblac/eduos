from celery import shared_task
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    ManagedFile, FileVersion, FileAccessLog, SharedAccess
)

logger = logging.getLogger(__name__)


@shared_task
def delete_expired_files():
    """
    Delete files that have passed their expiration date.
    """
    now = timezone.now()
    expired_files = ManagedFile.objects.filter(expires_at__lt=now, is_archived=False)
    for file in expired_files:
        try:
            default_storage.delete(file.file.name)
            file.is_archived = True
            file.save(update_fields = ['is_archived'])
            logger.info(f"Archived expired file: {file.name}")
        except Exception as e:
            logger.error(f"Error archiving file {file.id}: {e}")


@shared_task
def notify_users_of_new_file(file_id):
    """
    Send email notifications to users with shared access to a file.
    """
    try:
        file = ManagedFile.objects.get(id=file_id)
        recipients = set()

        # Get users from SharedAccess
        shares = SharedAccess.objects.filter(file=file)

        for share in shares:
            if share.user and share.user.email:
                recipients.add(share.user.email)

        recipients = list(recipients)

        if recipients:
            send_mail(
                subject=f"[EduOS] New File Shared: {file.name}",
                message=f"A new file '{file.name}' has been shared with you on EduOS.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=True
            )
            logger.info(f"Notification sent to {len(recipients)} users for file {file_id}")

    except ManagedFile.DoesNotExist:
        logger.error(f"File with id {file_id} does not exist.")


@shared_task
def log_file_download(file_id, user_id):
    """
    Log that a file was downloaded.
    """
    try:
        FileAccessLog.objects.create(
            file_id=file_id,
            user_id=user_id,
            action='downloaded'
        )
        logger.info(f"Logged download for file {file_id} by user {user_id}")
    except Exception as e:
        logger.error(f"Error logging file download: {e}")


@shared_task
def log_file_view(file_id, user_id):
    """
    Log that a file was viewed.
    """
    try:
        FileAccessLog.objects.create(
            file_id=file_id,
            user_id=user_id,
            action='viewed'
        )
        logger.info(f"Logged view for file {file_id} by user {user_id}")
    except Exception as e:
        logger.error(f"Error logging file view: {e}")


@shared_task
def clean_old_file_versions(days_old=90):
    """
    Delete old file versions older than `days_old` days.
    """
    cutoff_date = timezone.now() - timedelta(days=days_old)
    old_versions = FileVersion.objects.filter(uploaded_at__lt=cutoff_date)
    for version in old_versions:
        try:
            default_storage.delete(version.file.name)
            version.delete()
            logger.info(f"Deleted old version {version.id}")
        except Exception as e:
            logger.error(f"Error deleting old file version {version.id}: {e}")
