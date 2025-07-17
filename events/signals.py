from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Event
from notifications.models import Notification
from accounts.models import CustomUser
from students.models import Student


@receiver(post_save, sender=Event)
def notify_event_targets(sender, instance, created, **kwargs):
    if not created or not instance.is_active:
        return

    users = set()

    # Direct user targeting
    if instance.target_users.exists():
        users.update(instance.target_users.all())

    # Target by role
    if instance.target_roles:
        role_users = CustomUser.objects.filter(
            role__in=instance.target_roles,
            institution=instance.institution,
            is_active=True
        )
        users.update(role_users)

    # Target by class/stream/student
    student_qs = Student.objects.none()

    if instance.target_students.exists():
        student_qs |= instance.target_students.all()

    if instance.target_class_levels.exists():
        student_qs |= Student.objects.filter(
            class_level__in=instance.target_class_levels.all(),
            institution=instance.institution
        )

    if instance.target_streams.exists():
        student_qs |= Student.objects.filter(
            stream__in=instance.target_streams.all(),
            institution=instance.institution
        )

    # Add student.user to recipients
    student_users = CustomUser.objects.filter(
        id__in=student_qs.values_list('user_id', flat=True),
        is_active=True
    )
    users.update(student_users)

    if not users:
        return  # Avoid empty notifications

    # Create and dispatch notification
    notification = Notification.objects.create(
        institution=instance.institution,
        title=f"📅 New Event: {instance.title}",
        message=(
            f"You have been invited to a new *{instance.get_event_type_display()}* event:\n"
            f"**{instance.title}**\n"
            f"🕒 {instance.start_time.strftime('%A, %d %B %Y at %I:%M %p')}\n"
            f"{f'📍 Location: {instance.location}' if instance.location else ''}"
        ),
        notification_type='event',
        created_by=instance.created_by,
        is_active=True
    )

    notification.target_users.set(users)
    notification.channels = ["in_app", "email", "sms"]
    notification.save()
