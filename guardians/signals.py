from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Guardian, GuardianStudentLink
from notifications.utils import send_notification_to_user
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=Guardian)
def notify_guardian_account_created(sender, instance, created, **kwargs):
    if created:
        send_notification_to_user(
            user=instance.user,
            title="👨‍👩‍👧 Welcome to EduOS",
            message=f"Your guardian account at {instance.institution.name} has been successfully created."
        )


@receiver(post_save, sender=GuardianStudentLink)
def notify_guardian_student_link(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        relationship = instance.relationship or "Guardian"
        send_notification_to_user(
            user=instance.guardian.user,
            title="👧 Student Linked",
            message=f"You have been added as a {relationship} for {student.first_name} {student.last_name}."
        )


@receiver(pre_delete, sender=GuardianStudentLink)
def notify_guardian_student_unlink(sender, instance, **kwargs):
    student = instance.student
    send_notification_to_user(
        user=instance.guardian.user,
        title="🗑️ Student Unlinked",
        message=f"{student.first_name} {student.last_name} has been unlinked from your account."
    )
