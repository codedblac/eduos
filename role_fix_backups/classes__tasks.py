# classes/tasks.py

from celery import shared_task
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from institutions.models import Institution
from students.models import Student, StudentHistory
from .models import ClassLevel, Stream
from notifications.utils import send_notification_to_user

from .ai import (
    auto_assign_stream,
    suggest_balanced_allocation,
    recommend_class_for_transfer,
    generate_class_distribution_report
)

from .analytics import (
    get_class_level_distribution,
    get_stream_distribution,
    get_total_summary,
    get_enrollment_status_stats,
    get_overcrowded_streams
)


@shared_task
def promote_students_to_next_class(institution_id):
    """
    Promote eligible students in the institution to the next class level.
    """
    try:
        institution = Institution.objects.get(id=institution_id)
        class_levels = ClassLevel.objects.filter(institution=institution).order_by('order')
        class_level_map = {cl.order: cl for cl in class_levels}

        for student in Student.objects.filter(institution=institution, enrollment_status='active'):
            current_class = student.class_level
            if current_class and (current_class.order + 1) in class_level_map:
                next_class = class_level_map[current_class.order + 1]
                student.class_level = next_class
                student.save(update_fields = ['class_level'])

                StudentHistory.objects.create(
                    student=student,
                    changed_by=None,
                    change_type='Promoted',
                    old_class=current_class,
                    new_class=next_class,
                    old_stream=student.stream,
                    new_stream=student.stream,
                    notes='Automated promotion task'
                )
    except Institution.DoesNotExist:
        pass


@shared_task
def check_stream_overcapacity():
    """
    Identify and notify admins of overcapacity streams.
    """
    THRESHOLD = 50

    over_capacity_streams = Stream.objects.annotate(student_count=Count('students')).filter(student_count__gt=THRESHOLD)
    for stream in over_capacity_streams:
        institution = stream.institution
        admins = institution.customuser_set.filter(is_staff=True)
        for admin in admins:
            send_notification_to_user(
                admin,
                title="Overcapacity Alert",
                message=(
                    f"Stream '{stream.name}' in '{stream.class_level.name}' has "
                    f"{stream.students.count()} students (Threshold: {THRESHOLD})."
                )
            )


@shared_task
def auto_assign_students_to_streams(institution_id):
    """
    Assign students without a stream to the least-populated one.
    """
    students = Student.objects.filter(institution_id=institution_id, stream__isnull=True, class_level__isnull=False)
    for student in students:
        auto_assign_stream(student)


@shared_task
def redistribute_students_for_balance(institution_id):
    """
    Redistribute students between streams to balance overloaded and underloaded streams.
    """
    institution = Institution.objects.get(id=institution_id)
    suggestions = suggest_balanced_allocation(institution)
    admins = institution.customuser_set.filter(is_staff=True)

    for suggestion in suggestions:
        for admin in admins:
            send_notification_to_user(
                admin,
                title="Stream Imbalance Detected",
                message=(
                    f"Suggestion: Move ~{suggestion['students_to_move']} students from "
                    f"'{suggestion['from_stream']}' to '{suggestion['to_stream']}' in "
                    f"class level '{suggestion['class_level']}'."
                )
            )


@shared_task
def archive_old_streams():
    """
    Archive streams that haven't been updated in over 3 years.
    Assumes you have an 'archived' field in the model.
    """
    cutoff_date = timezone.now() - timedelta(days=3*365)
    Stream.objects.filter(updated_at__lt=cutoff_date).update(is_active=False)


@shared_task
def generate_class_insights(institution_id):
    """
    Generate AI + analytics insights about a school’s classes and notify admins.
    """
    institution = Institution.objects.get(id=institution_id)
    admins = institution.customuser_set.filter(is_staff=True)

    # Run analytics and AI together
    class_distribution = generate_class_distribution_report(institution)
    class_level_stats = get_class_level_distribution(institution_id)
    stream_stats = get_stream_distribution(institution_id)
    summary = get_total_summary(institution_id)
    enrollment_stats = get_enrollment_status_stats(institution_id)
    overcrowded = get_overcrowded_streams(institution_id)
    
    # Optionally: store these in a DB table, or email/downloadable report
    for admin in admins:
        send_notification_to_user(
            admin,
            title="📊 Class AI Insights Ready",
            message=(
                f"Class stats and trends generated for {institution.name}. "
                f"Total students: {summary['total_students']}, Classes: {summary['total_classes']}, "
                f"Streams: {summary['total_streams']}, Teachers assigned: {summary['teachers_with_assigned_students']}."
            )
        )
