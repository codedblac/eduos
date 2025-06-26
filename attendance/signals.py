from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClassAttendanceRecord, SchoolAttendanceRecord, AttendanceStatus
from notifications.models import Notification
from students.models import Student
from accounts.models import CustomUser
from django.utils.timezone import now


def notify_guardians(student, title, message):
    guardians = student.guardian_set.all()
    for guardian in guardians:
        Notification.objects.create(
            institution=student.institution,
            title=title,
            message=message,
            notification_type='student_attendance',
            created_by=None,
            is_active=True,
        ).target_users.add(guardian.user)


def notify_admins(institution, title, message):
    admins = CustomUser.objects.filter(role='admin', institution=institution)
    for admin in admins:
        Notification.objects.create(
            institution=institution,
            title=title,
            message=message,
            notification_type='teacher_absence',
            created_by=None,
            is_active=True,
        ).target_users.add(admin)


@receiver(post_save, sender=ClassAttendanceRecord)
def handle_class_attendance(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.student and instance.status == AttendanceStatus.ABSENT:
        notify_guardians(
            student=instance.student,
            title="Class Absence Alert",
            message=f"{instance.student.full_name} missed {instance.subject} on {instance.date}."
        )

    if instance.teacher and instance.status == AttendanceStatus.ABSENT:
        notify_admins(
            institution=instance.institution,
            title="Teacher Missed Lesson",
            message=f"{instance.teacher.get_full_name()} missed teaching {instance.subject} on {instance.date}."
        )


@receiver(post_save, sender=SchoolAttendanceRecord)
def handle_school_attendance(sender, instance, created, **kwargs):
    if not created:
        return

    # Notify only for students
    if hasattr(instance.user, 'student'):
        student = instance.user.student
        if instance.entry_time:
            notify_guardians(
                student=student,
                title="School Entry Recorded",
                message=f"{student.full_name} entered school at {instance.entry_time} on {instance.date}."
            )
        if instance.exit_time:
            notify_guardians(
                student=student,
                title="School Exit Recorded",
                message=f"{student.full_name} exited school at {instance.exit_time} on {instance.date}."
            )
