from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Student, MedicalFlag
from .tasks import run_ai_analysis_on_students, notify_critical_medical_flags
from notifications.utils import send_notification_to_user
import uuid


@receiver(pre_save, sender=Student)
def generate_admission_number(sender, instance, **kwargs):
    """
    Auto-generate an admission number if not set (optional logic).
    Assumes format: INSTYYYYXXXX
    """
    if not instance.admission_number:
        year = timezone.now().year
        uid = uuid.uuid4().hex[:6].upper()
        instance.admission_number = f"{instance.institution.id}{year}{uid}"


@receiver(post_save, sender=Student)
def run_ai_and_notify_on_student_save(sender, instance, created, **kwargs):
    """
    Trigger AI analysis and notify institution staff upon student creation/update.
    """
    if created:
        # Notify admins
        admins = instance.institution.customuser_set.filter(is_staff=True)
        for admin in admins:
            send_notification_to_user(
                admin,
                title="New Student Registered",
                message=f"{instance} has been admitted to {instance.institution.name}."
            )

    # Trigger async AI analysis
    run_ai_analysis_on_students.delay(institution_id=instance.institution.id)


@receiver(post_save, sender=MedicalFlag)
def notify_critical_medical_flag(sender, instance, created, **kwargs):
    """
    Notify institution staff when a critical medical flag is added.
    """
    if created and instance.critical:
        student = instance.student
        admins = student.institution.customuser_set.filter(is_staff=True)
        for admin in admins:
            send_notification_to_user(
                admin,
                title="Critical Medical Flag",
                message=f"{student} has a critical condition: {instance.condition}."
            )
