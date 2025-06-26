from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, NotificationDelivery, NotificationChannel
from accounts.models import CustomUser
from students.models import Student

def get_notification_recipients(notification):
    institution = notification.institution
    recipients = set()

    # Directly targeted users
    if notification.target_users.exists():
        recipients.update(notification.target_users.all())

    # Role-based targeting
    if notification.target_roles:
        recipients.update(
            CustomUser.objects.filter(role__in=notification.target_roles, institution=institution)
        )

    # Class level targeting
    if notification.target_class_levels.exists():
        students = Student.objects.filter(class_level__in=notification.target_class_levels.all(), institution=institution)
        recipients.update([s.user for s in students if s.user])

    # Stream targeting
    if notification.target_streams.exists():
        students = Student.objects.filter(stream__in=notification.target_streams.all(), institution=institution)
        recipients.update([s.user for s in students if s.user])

    # Student-specific targeting
    if notification.target_students.exists():
        recipients.update([s.user for s in notification.target_students.all() if s.user])

    return list(recipients)


@receiver(post_save, sender=Notification)
def create_deliveries_on_notification(sender, instance, created, **kwargs):
    if not created:
        return

    recipients = get_notification_recipients(instance)
    deliveries = []

    for user in recipients:
        for channel in instance.channels:
            deliveries.append(NotificationDelivery(
                notification=instance,
                user=user,
                channel=channel,
                delivered=False,
                read=False
            ))

    NotificationDelivery.objects.bulk_create(deliveries)
