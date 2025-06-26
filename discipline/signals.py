from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DisciplineCase
from notifications.models import Notification
from guardians.models import GuardianStudentLink



@receiver(post_save, sender=DisciplineCase)
def notify_guardians_on_discipline(sender, instance, created, **kwargs):
    if not created:
        return

    student = instance.student
    guardians = GuardianStudentLink.objects.filter(student=student, is_active=True).select_related('guardian')

    title = "Discipline Case Alert"
    message = f"{student.full_name} was involved in a {instance.severity.upper()} case: {instance.category.name} on {instance.incident_date}."

    for link in guardians:
        Notification.objects.create(
            institution=instance.institution,
            title=title,
            message=message,
            notification_type="discipline",
            created_by=instance.reported_by,
        ).target_users.add(link.guardian.user)
