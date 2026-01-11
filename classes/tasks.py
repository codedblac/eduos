# classes/tasks.py

from celery import shared_task
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from institutions.models import Institution
from students.models import Student, StudentStreamEnrollment, StudentHistory
from notifications.utils import send_notification_to_user
from .ai import (
    auto_assign_stream,
    suggest_balanced_allocation,
    generate_class_distribution_report
)
from .analytics import (
    get_class_level_distribution,
    get_stream_distribution,
    get_total_summary,
    get_enrollment_status_stats,
    get_overcrowded_streams
)

# ======================================================
# 🔹 Recompute Stream Analytics
# ======================================================
@shared_task
def recompute_stream_analytics(stream_id, academic_year_id):
    from .models import Stream, StreamAnalytics  # Local import to avoid circular imports

    try:
        stream = Stream.objects.get(id=stream_id)
        active_students_count = stream.enrollments.filter(status='active').count()

        # Placeholder analytics, extend as needed
        StreamAnalytics.objects.update_or_create(
            stream=stream,
            academic_year_id=academic_year_id,
            defaults={
                'total_students': active_students_count,
                'average_score': 0,       # TODO: compute actual score
                'attendance_rate': 0,     # TODO: compute actual attendance
                'discipline_index': 0     # TODO: compute discipline metric
            }
        )
    except Stream.DoesNotExist:
        pass


# ======================================================
# 🔹 Recompute Class Level Analytics
# ======================================================
@shared_task
def recompute_class_level_analytics(class_level_id, academic_year_id):
    from .models import ClassLevel, ClassLevelAnalytics, Stream  # Local import

    try:
        class_level = ClassLevel.objects.get(id=class_level_id)
        streams = Stream.objects.filter(class_level=class_level, academic_year_id=academic_year_id)
        total_students = sum([s.enrollments.filter(status='active').count() for s in streams])
        top_stream = max(streams, key=lambda s: s.enrollments.filter(status='active').count(), default=None)

        ClassLevelAnalytics.objects.update_or_create(
            class_level=class_level,
            academic_year_id=academic_year_id,
            defaults={
                'total_students': total_students,
                'average_score': 0,  # TODO: compute real average
                'top_stream': top_stream
            }
        )
    except ClassLevel.DoesNotExist:
        pass


# ======================================================
# 🔹 Promote Students to Next ClassLevel
# ======================================================
@shared_task
def promote_students_to_next_class(institution_id, academic_year_id):
    """
    Promote eligible students to the next class level.
    Creates new StudentStreamEnrollment records for the next year.
    """
    try:
        institution = Institution.objects.get(id=institution_id)
        class_levels = institution.class_levels.all().order_by('order')
        class_level_map = {cl.order: cl for cl in class_levels}

        students = Student.objects.filter(institution=institution, enrollment_status='active')

        for student in students:
            current_class = student.class_level
            if not current_class:
                continue

            next_order = current_class.order + 1
            if next_order not in class_level_map:
                continue

            next_class = class_level_map[next_order]

            # Record history
            old_enrollments = StudentStreamEnrollment.objects.filter(
                student=student,
                academic_year_id=academic_year_id,
                status='active'
            )
            old_stream = old_enrollments.first().stream if old_enrollments.exists() else None

            # Deactivate old enrollment
            old_enrollments.update(status='promoted')

            # Create new enrollment for next year
            StudentStreamEnrollment.objects.create(
                student=student,
                class_level=next_class,
                academic_year_id=academic_year_id,
                status='active'
            )

            StudentHistory.objects.create(
                student=student,
                changed_by=None,
                change_type='Promoted',
                old_class=current_class,
                new_class=next_class,
                old_stream=old_stream,
                new_stream=None,
                notes='Automated promotion task'
            )

    except Institution.DoesNotExist:
        pass


# ======================================================
# 🔹 Auto Assign Students Without Stream
# ======================================================
@shared_task
def auto_assign_students_to_streams(institution_id, academic_year_id):
    """
    Assign students without a stream to the least-populated one for the given year.
    """
    students = StudentStreamEnrollment.objects.filter(
        student__institution_id=institution_id,
        academic_year_id=academic_year_id,
        stream__isnull=True,
        status='active'
    )

    for enrollment in students:
        auto_assign_stream(
            student=enrollment.student,
            class_level=enrollment.class_level,
            academic_year_id=academic_year_id,
            assigned_by=None
        )


# ======================================================
# 🔹 Redistribute Students for Balance
# ======================================================
@shared_task
def redistribute_students_for_balance(institution_id, academic_year_id):
    """
    Notify admins of stream balancing suggestions for a given year.
    """
    try:
        institution = Institution.objects.get(id=institution_id)
        suggestions = suggest_balanced_allocation(institution=institution, academic_year_id=academic_year_id)
        admins = institution.customuser_set.filter(is_staff=True)

        for suggestion in suggestions:
            for admin in admins:
                send_notification_to_user(
                    admin,
                    title="Stream Imbalance Detected",
                    message=(
                        f"Suggestion: Move ~{suggestion['students_to_move']} students from "
                        f"'{suggestion['from_stream']}' to '{suggestion['to_stream']}' in "
                        f"class level '{suggestion['class_level']}' for {academic_year_id}."
                    )
                )
    except Institution.DoesNotExist:
        pass


# ======================================================
# 🔹 Archive Old Streams
# ======================================================
@shared_task
def archive_old_streams():
    """
    Archive streams that haven't been updated in over 3 years.
    """
    cutoff_date = timezone.now() - timedelta(days=3*365)
    Stream.objects.filter(updated_at__lt=cutoff_date).update(is_active=False)


# ======================================================
# 🔹 Generate Class Insights (AI + Analytics)
# ======================================================
@shared_task
def generate_class_insights(institution_id, academic_year_id):
    """
    Generate AI + analytics insights about a school’s classes for the given year.
    Stores analytics and notifies admins.
    """
    try:
        institution = Institution.objects.get(id=institution_id)
        admins = institution.customuser_set.filter(is_staff=True)

        # Analytics
        generate_class_distribution_report(institution=institution, academic_year_id=academic_year_id)
        get_class_level_distribution(institution_id)
        get_stream_distribution(institution_id)
        summary = get_total_summary(institution_id)
        get_enrollment_status_stats(institution_id)
        get_overcrowded_streams(institution_id)

        # Notify admins
        for admin in admins:
            send_notification_to_user(
                admin,
                title="📊 Class AI Insights Ready",
                message=(
                    f"Class stats and trends generated for {institution.name} ({academic_year_id}). "
                    f"Total students: {summary['total_students']}, Classes: {summary['total_classes']}, "
                    f"Streams: {summary['total_streams']}, Teachers assigned: {summary['total_teachers']}."
                )
            )
    except Institution.DoesNotExist:
        pass
