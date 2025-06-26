from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event
from notifications.models import Notification
from accounts.models import CustomUser
from students.models import Student
from django.utils import timezone
import datetime

@receiver(post_save, sender=Event)
def notify_event_targets(sender, instance, created, **kwargs):
    if not created:
        return  # Notify only on creation

    users = set()

    # Direct user targeting
    users.update(instance.target_users.all())

    # Target by role
    if instance.target_roles:
        role_users = CustomUser.objects.filter(
            role__in=instance.target_roles,
            institution=instance.institution
        )
        users.update(role_users)

    # Target by class/stream
    student_qs = Student.objects.none()

    if instance.target_students.exists():
        student_qs |= instance.target_students.all()
    if instance.target_class_levels.exists():
        student_qs |= Student.objects.filter(class_level__in=instance.target_class_levels.all())
    if instance.target_streams.exists():
        student_qs |= Student.objects.filter(stream__in=instance.target_streams.all())

    student_users = CustomUser.objects.filter(id__in=[s.user_id for s in student_qs])
    users.update(student_users)

    # Create notification
    notification = Notification.objects.create(
        institution=instance.institution,
        title=f"New Event: {instance.title}",
        message=(
            f"You have been invited to a new {instance.get_event_type_display()} event titled '{instance.title}' "
            f"scheduled for {instance.start_time.strftime('%d %b %Y, %I:%M %p')}."
        ),
        notification_type='event',
        created_by=instance.created_by,
        target_users=list(users),
        target_roles=None,
        channels=["in_app", "email", "sms"]
    )
