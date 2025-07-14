from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AdmissionOffer, Applicant, AdmissionComment
from notifications.utils import send_notification_to_user
import logging

logger = logging.getLogger(__name__)


def safe_notify(user, title, message):
    """
    Sends notification safely with logging.
    """
    try:
        if user and user.is_active:
            send_notification_to_user(user, title=title, message=message)
            logger.info(f"[Admissions] Notification sent to {user}: {title}")
    except Exception as e:
        logger.error(f"[Admissions] Failed to send notification to {user}: {e}")


@receiver(post_save, sender=AdmissionOffer)
def notify_applicant_of_offer(sender, instance, created, **kwargs):
    """
    Notify applicant when a new admission offer is created.
    """
    if created:
        user = getattr(instance.applicant, 'user', None)
        if user:
            safe_notify(
                user,
                title="🎓 Admission Offer Issued",
                message=f"You have received an admission offer. Please respond before {instance.expiry_date}."
            )


@receiver(post_save, sender=Applicant)
def notify_applicant_status_change(sender, instance, **kwargs):
    """
    Notify applicant on status changes like shortlisted, accepted, or rejected.
    """
    if instance.application_status in ['shortlisted', 'accepted', 'rejected']:
        user = getattr(instance, 'user', None)
        if user:
            safe_notify(
                user,
                title="📢 Admission Status Update",
                message=f"Your application status is now: {instance.application_status.title()}."
            )


@receiver(post_save, sender=AdmissionComment)
def notify_staff_of_comment(sender, instance, created, **kwargs):
    """
    Notify institution staff when a new comment is added to an applicant.
    """
    if created and instance.applicant and instance.applicant.admission_session:
        staff_qs = instance.applicant.admission_session.institution.customuser_set.filter(is_staff=True)
        notified_count = 0
        for staff_user in staff_qs:
            safe_notify(
                staff_user,
                title=f"💬 New Comment on Applicant {instance.applicant}",
                message=f"{instance.author} wrote: {instance.comment[:100]}..."
            )
            notified_count += 1
        logger.info(f"[Admissions] Notified {notified_count} staff members of new comment.")
