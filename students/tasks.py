# students/tasks.py

from celery import shared_task
from django.utils import timezone
from .models import Student, StudentHistory, MedicalFlag
from .ai import StudentAIAnalyzer
from notifications.utils import send_notification_to_user
from django.db.models import Q


@shared_task
def run_ai_analysis_on_students(institution_id):
    """
    Run AI analysis for all active students in an institution.
    Updates AI summary fields.
    """
    students = Student.objects.filter(
        institution_id=institution_id,
        enrollment_status='active'
    )

    for student in students:
        analyzer = StudentAIAnalyzer(student)
        result = analyzer.run_full_analysis()

        student.ai_insights = "\n".join(result.get("insights", []))
        student.performance_comments = result.get("feedback_comment", "")
        student.recommended_books = student.recommended_books or []
        student.recommended_teachers = student.recommended_teachers or []
        student.save(update_fields = [
            "ai_insights", "performance_comments", "recommended_books", "recommended_teachers"
        ])


@shared_task
def promote_students():
    """
    Promote all eligible students to the next class_level, if applicable.
    """
    eligible_students = Student.objects.filter(
        enrollment_status='active',
        class_level__isnull=False
    ).select_related('class_level')

    for student in eligible_students:
        current_level = student.class_level
        next_level = current_level.default_promotion_class
        if next_level:
            old_level = student.class_level
            student.class_level = next_level
            student.save(update_fields = ['class_level'])

            StudentHistory.objects.create(
                student=student,
                changed_by=None,
                change_type='Promoted',
                old_class=old_level,
                new_class=next_level,
                old_stream=student.stream,
                new_stream=student.stream,
                notes="Auto-promotion task"
            )


@shared_task
def notify_critical_medical_flags():
    """
    Send alert notifications for students with critical medical conditions.
    Can be triggered weekly/daily.
    """
    flags = MedicalFlag.objects.filter(critical=True).select_related("student")

    for flag in flags:
        student = flag.student
        institution = student.institution
        admins = institution.customuser_set.filter(is_staff=True)

        for admin in admins:
            send_notification_to_user(
                user=admin,
                title="Critical Medical Alert",
                message=f"{student} has a critical medical condition: {flag.condition}."
            )


@shared_task
def identify_transfer_candidates():
    """
    Detect students who haven't been active in the last 90 days.
    (Could be marked as transferred or inactive.)
    """
    cutoff = timezone.now().date() - timezone.timedelta(days=90)
    inactive_students = Student.objects.filter(
        Q(date_left__isnull=False, date_left__lt=cutoff) |
        Q(enrollment_status='active', date_joined__lt=cutoff, stream__isnull=True)
    )

    for student in inactive_students:
        student.enrollment_status = 'inactive'
        student.save(update_fields = ['enrollment_status'])

        StudentHistory.objects.create(
            student=student,
            change_type='Marked Inactive',
            changed_by=None,
            notes="Automatically marked due to inactivity"
        )


@shared_task
def assign_streams_for_unplaced_students():
    """
    Automatically assigns streams to students without one based on least population.
    """
    students = Student.objects.filter(
        stream__isnull=True,
        class_level__isnull=False,
        enrollment_status='active'
    )

    for student in students:
        analyzer = StudentAIAnalyzer(student)
        assigned = analyzer.auto_assign_stream()
