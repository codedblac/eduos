from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClassAttendanceRecord, SchoolAttendanceRecord, AttendanceStatus
from notifications.models import Notification
from students.models import Student
from accounts.models import CustomUser
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)


def notify_guardians(student, title, message):
    guardians = getattr(student, 'guardian_set', None)
    if guardians:
        for guardian in guardians.all():
            notification, created = Notification.objects.get_or_create(
                institution=student.institution,
                title=title,
                message=message,
                notification_type='student_attendance',
                created_by=None,
                is_active=True,
            )
            notification.target_users.add(guardian.user)
            logger.info(f"Notification sent to guardian of {student.full_name}")


def notify_admins(institution, title, message):
    admins = CustomUser.objects.filter(role='ADMIN', institution=institution, is_active=True)
    for admin in admins:
        notification, created = Notification.objects.get_or_create(
            institution=institution,
            title=title,
            message=message,
            notification_type='teacher_absence',
            created_by=None,
            is_active=True,
        )
        notification.target_users.add(admin)
        logger.info(f"Notification sent to admin: {admin.get_full_name()}")


@receiver(post_save, sender=ClassAttendanceRecord)
def handle_class_attendance(sender, instance, created, **kwargs):
    if not created:
        return

    # Student absent
    if instance.student and instance.status == AttendanceStatus.ABSENT:
        subject_name = instance.subject.name if instance.subject else "a lesson"
        notify_guardians(
            student=instance.student,
            title="Class Absence Alert",
            message=f"{instance.student.full_name} missed {subject_name} on {instance.date}."
        )

    # Teacher absent
    if instance.teacher and instance.status == AttendanceStatus.ABSENT:
        subject_name = instance.subject.name if instance.subject else "a lesson"
        notify_admins(
            institution=instance.institution,
            title="Teacher Missed Lesson",
            message=f"{instance.teacher.get_full_name()} missed teaching {subject_name} on {instance.date}."
        )


@receiver(post_save, sender=SchoolAttendanceRecord)
def handle_school_attendance(sender, instance, created, **kwargs):
    if not created:
        return

    # Handle only students
    if hasattr(instance.user, 'student'):
        student = instance.user.student
        if instance.entry_time:
            notify_guardians(
                student=student,
                title="School Entry Recorded",
                message=f"{student.full_name} entered school at {instance.entry_time.strftime('%H:%M')} on {instance.date}."
            )
        if instance.exit_time:
            notify_guardians(
                student=student,
                title="School Exit Recorded",
                message=f"{student.full_name} exited school at {instance.exit_time.strftime('%H:%M')} on {instance.date}."
            )
