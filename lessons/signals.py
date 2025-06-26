from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LessonSession, LessonAttachment
from notifications.utils import send_notification_to_user as notify_user



@receiver(post_save, sender=LessonSession)
def notify_on_lesson_session_created(sender, instance, created, **kwargs):
    if created and instance.lesson_schedule.lesson_plan.teacher:
        notify_user(
            instance.lesson_schedule.lesson_plan.teacher,
            f"Your lesson session on {instance.delivered_on} has been recorded."
        )


@receiver(post_save, sender=LessonAttachment)
def notify_on_attachment_uploaded(sender, instance, created, **kwargs):
    if created and instance.lesson_session and instance.lesson_session.lesson_schedule.lesson_plan.teacher:
        notify_user(
            instance.lesson_session.lesson_schedule.lesson_plan.teacher,
            f"A new resource '{instance.title}' was uploaded for your lesson on {instance.lesson_session.delivered_on}."
        )
