from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AdmissionOffer, Applicant, AdmissionComment
from notifications.utils import send_notification_to_user


@receiver(post_save, sender=AdmissionOffer)
def notify_applicant_of_offer(sender, instance, created, **kwargs):
    if created and instance.applicant:
        user = getattr(instance.applicant, 'user', None)
        if user:
            send_notification_to_user(
                user,
                title="Admission Offer Issued",
                message=f"You have received an admission offer. Please review and respond before {instance.expiry_date}."
            )


@receiver(post_save, sender=Applicant)
def notify_status_change(sender, instance, **kwargs):
    if instance.application_status in ['accepted', 'rejected', 'shortlisted']:
        user = getattr(instance, 'user', None)
        if user:
            send_notification_to_user(
                user,
                title="Admission Status Update",
                message=f"Your application status has been updated to: {instance.application_status.title()}"
            )


@receiver(post_save, sender=AdmissionComment)
def notify_staff_of_comment(sender, instance, created, **kwargs):
    if created and instance.applicant:
        admission_team = instance.applicant.admission_session.institution.customuser_set.filter(is_staff=True)
        for staff_user in admission_team:
            send_notification_to_user(
                staff_user,
                title=f"New Comment on Applicant {instance.applicant}",
                message=f"{instance.author} commented: {instance.comment[:100]}..."
            )
