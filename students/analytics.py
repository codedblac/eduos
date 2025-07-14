from django.db.models import Count, F, Q
from students.models import Student
from classes.models import ClassLevel, Stream


def get_class_level_distribution(institution_id):
    """
    Returns student count per class level.
    """
    return Student.objects.filter(institution_id=institution_id).values(
        class_level=F("class_level__name")
    ).annotate(
        count=Count("id")
    ).order_by("class_level")


def get_stream_distribution(institution_id):
    """
    Returns student count per stream and class level.
    """
    return Student.objects.filter(institution_id=institution_id).values(
        class_level=F("class_level__name"),
        stream=F("stream__name")
    ).annotate(
        count=Count("id")
    ).order_by("class_level", "stream")


def get_gender_breakdown_per_class(institution_id):
    """
    Gender distribution per class level.
    """
    return Student.objects.filter(institution_id=institution_id).values(
        class_level=F("class_level__name"),
        gender=F("gender")
    ).annotate(
        count=Count("id")
    ).order_by("class_level", "gender")


def get_overcrowded_streams(institution_id, threshold=45):
    """
    Streams that exceed defined student capacity.
    """
    return Stream.objects.filter(
        class_level__institution_id=institution_id
    ).annotate(
        student_count=Count("students")
    ).filter(
        student_count__gt=threshold
    ).values(
        "id", "name", "class_level__name", "student_count"
    ).order_by("-student_count")


def get_empty_classes_and_streams(institution_id):
    """
    Detect class levels or streams with no students.
    """
    empty_classes = ClassLevel.objects.filter(
        institution_id=institution_id
    ).annotate(
        student_count=Count("students")
    ).filter(student_count=0).values("id", "name")

    empty_streams = Stream.objects.filter(
        class_level__institution_id=institution_id
    ).annotate(
        student_count=Count("students")
    ).filter(student_count=0).values("id", "name", "class_level__name")

    return {
        "empty_class_levels": list(empty_classes),
        "empty_streams": list(empty_streams)
    }


def get_enrollment_status_stats(institution_id):
    """
    Returns count of students by enrollment status.
    """
    return Student.objects.filter(institution_id=institution_id).values(
        "enrollment_status"
    ).annotate(
        count=Count("id")
    ).order_by("-count")


def get_total_summary(institution_id):
    """
    Summary metrics for dashboards and quick stats.
    """
    total_students = Student.objects.filter(institution_id=institution_id).count()
    total_classes = ClassLevel.objects.filter(institution_id=institution_id).count()
    total_streams = Stream.objects.filter(class_level__institution_id=institution_id).count()
    assigned_teachers = Student.objects.filter(
        institution_id=institution_id,
        assigned_class_teacher__isnull=False
    ).values("assigned_class_teacher").distinct().count()

    return {
        "total_students": total_students,
        "total_classes": total_classes,
        "total_streams": total_streams,
        "teachers_with_assigned_students": assigned_teachers
    }
