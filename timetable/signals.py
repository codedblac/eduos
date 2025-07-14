from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import TimetableEntry
from attendance.models import ClassAttendanceRecord
from notifications.utils import send_notification_to_user
from .tasks import auto_reschedule_absent_teachers

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TimetableEntry)
def notify_teacher_on_timetable_entry(sender, instance, created, **kwargs):
    """
    Notify teacher when a new or updated timetable entry is saved.
    """
    try:
        teacher = instance.teacher
        period = instance.period_template

        message = (
            f"{'🆕 New' if created else '🔄 Updated'} lesson:\n"
            f"{instance.subject.name} - {instance.stream.name}\n"
            f"⏰ {period.day}, {period.start_time.strftime('%H:%M')} - {period.end_time.strftime('%H:%M')}"
        )

        send_notification_to_user(
            user=teacher.user,
            title="Timetable Update",
            message=message,
            channel="in_app"
        )
    except Exception as e:
        logger.warning(f"Error sending timetable notification: {e}")


@receiver(post_save, sender=ClassAttendanceRecord)
def handle_absent_teacher_reschedule(sender, instance, created, **kwargs):
    """
    If a teacher marks themselves absent, trigger auto-substitution task.
    """
    if created and not instance.resolved:
        try:
            auto_reschedule_absent_teachers.delay()
        except Exception as e:
            logger.error(f"Failed to dispatch auto-reschedule task: {e}")
