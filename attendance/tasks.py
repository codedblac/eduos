import datetime
import logging
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail

from .models import (
    SchoolAttendanceRecord,
    ClassAttendanceRecord,
    AbsenceReason
)
from students.models import Student
from accounts.models import CustomUser
from institutions.models import Institution

logger = logging.getLogger(__name__)


def auto_flag_absentees(institution_id=None, grace_hour=9):
    """
    Automatically flag students or staff as absent if they haven't checked in by a certain time.
    """
    today = timezone.localdate()
    current_time = timezone.localtime().time()
    cutoff = datetime.time(hour=grace_hour)

    if current_time < cutoff:
        logger.info("Grace period still active. Skipping absentee auto-flag.")
        return

    institutions = Institution.objects.filter(id=institution_id) if institution_id else Institution.objects.all()

    for institution in institutions:
        users = CustomUser.objects.filter(institution=institution, is_active=True)
        students = Student.objects.filter(institution=institution, is_active=True)

        # Flag missing staff
        for user in users:
            if not SchoolAttendanceRecord.objects.filter(user=user, date=today).exists():
                SchoolAttendanceRecord.objects.create(
                    institution=institution,
                    user=user,
                    date=today,
                    source='manual',
                    recorded_by=None,
                    entry_time=None
                )
                logger.warning(f"Staff {user} auto-flagged as absent for {today}")

        # Flag missing students
        for student in students:
            if not ClassAttendanceRecord.objects.filter(student=student, date=today).exists():
                ClassAttendanceRecord.objects.create(
                    institution=institution,
                    student=student,
                    date=today,
                    status='absent',
                    source='manual',
                    recorded_by=None,
                    class_level=student.class_level,
                    stream=student.stream,
                    reason=AbsenceReason.objects.filter(institution=institution, default=True).first()
                )
                logger.warning(f"Student {student} auto-flagged as absent for {today}")


def send_daily_attendance_summary():
    """
    Email daily attendance summaries to HR/admins.
    """
    today = timezone.localdate()
    institutions = Institution.objects.all()

    for inst in institutions:
        staff_total = CustomUser.objects.filter(institution=inst, is_active=True).count()
        staff_present = SchoolAttendanceRecord.objects.filter(
            institution=inst, date=today
        ).exclude(entry_time__isnull=True).count()

        students_total = Student.objects.filter(institution=inst, is_active=True).count()
        students_present = ClassAttendanceRecord.objects.filter(
            institution=inst, date=today, status='present'
        ).count()

        subject = f"[Attendance Summary] {inst.name} - {today}"
        message = (
            f"STAFF: {staff_present}/{staff_total} present\n"
            f"STUDENTS: {students_present}/{students_total} present"
        )

        admins = CustomUser.objects.filter(institution=inst, primary_role='ADMIN', is_active=True)
        to_emails = [admin.email for admin in admins if admin.email]

        if to_emails:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to_emails)
            logger.info(f"Sent daily summary to {inst.name} admins.")


def archive_old_attendance(days=365):
    """
    Optional: archive or delete attendance records older than X days.
    """
    cutoff = timezone.now() - datetime.timedelta(days=days)
    school_qs = SchoolAttendanceRecord.objects.filter(date__lt=cutoff)
    class_qs = ClassAttendanceRecord.objects.filter(date__lt=cutoff)

    school_deleted, _ = school_qs.delete()
    class_deleted, _ = class_qs.delete()

    logger.info(f"Archived {school_deleted} school and {class_deleted} class attendance records older than {days} days.")
