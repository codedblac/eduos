from django.db.models import Count, F
from typing import Dict, List, Any
from .models import ClassLevel, Stream
from students.models import Student
from teachers.models import Teacher
from institutions.models import Institution


def get_class_level_distribution(institution_id: int) -> List[Dict[str, Any]]:
    """
    Returns number of students per class level for a given institution.
    """
    return (
        Student.objects.filter(institution_id=institution_id)
        .values(class_level=F("class_level__name"))
        .annotate(count=Count("id"))
        .order_by("class_level")
    )


def get_stream_distribution(institution_id: int) -> List[Dict[str, Any]]:
    """
    Returns number of students per stream within each class level.
    """
    return (
        Student.objects.filter(institution_id=institution_id)
        .values(
            class_level=F("class_level__name"),
            stream=F("stream__name")
        )
        .annotate(count=Count("id"))
        .order_by("class_level", "stream")
    )


def get_gender_breakdown_per_class(institution_id: int) -> List[Dict[str, Any]]:
    """
    Returns gender distribution grouped by class level.
    """
    return (
        Student.objects.filter(institution_id=institution_id)
        .values(
            class_level=F("class_level__name"),
            gender=F("gender")
        )
        .annotate(count=Count("id"))
        .order_by("class_level", "gender")
    )


def get_overcrowded_streams(institution_id: int, threshold: int = 45) -> List[Dict[str, Any]]:
    """
    Detect streams exceeding the specified student threshold.
    """
    return (
        Stream.objects.filter(class_level__institution_id=institution_id)
        .annotate(student_count=Count("students"))
        .filter(student_count__gt=threshold)
        .values(
            "id", "name", "code", 
            "class_level__name", 
            "student_count", "capacity"
        )
        .order_by("-student_count")
    )


def get_empty_classes_and_streams(institution_id: int) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns lists of empty class levels and empty streams (zero students).
    """
    empty_classes = ClassLevel.objects.filter(institution_id=institution_id)\
        .annotate(student_count=Count("students"))\
        .filter(student_count=0)\
        .values("id", "name", "code")

    empty_streams = Stream.objects.filter(class_level__institution_id=institution_id)\
        .annotate(student_count=Count("students"))\
        .filter(student_count=0)\
        .values("id", "name", "code", "class_level__name")

    return {
        "empty_class_levels": list(empty_classes),
        "empty_streams": list(empty_streams)
    }


def get_total_summary(institution_id: int) -> Dict[str, int]:
    """
    Returns a summary of key totals for dashboard metrics.
    """
    total_students = Student.objects.filter(institution_id=institution_id).count()
    total_classes = ClassLevel.objects.filter(institution_id=institution_id).count()
    total_streams = Stream.objects.filter(institution_id=institution_id).count()
    total_teachers = Teacher.objects.filter(institution_id=institution_id).count()

    return {
        "total_students": total_students,
        "total_classes": total_classes,
        "total_streams": total_streams,
        "total_teachers": total_teachers,
    }


def get_enrollment_status_stats(institution_id: int) -> List[Dict[str, Any]]:
    """
    Returns student counts grouped by enrollment status.
    """
    return (
        Student.objects.filter(institution_id=institution_id)
        .values("enrollment_status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
