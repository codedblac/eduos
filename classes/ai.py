# classes/ai.py

from typing import Optional, List, Dict
import random

from django.db.models import Count, Q, F

from .models import (
    ClassLevel,
    Stream,
    StudentStreamEnrollment,
    StreamAnalytics,
)
from students.models import Student
from academics.models import AcademicYear


# ======================================================
# 🔹 STREAM RECOMMENDATIONS
# ======================================================

def recommend_least_populated_stream(
    class_level: ClassLevel,
    academic_year: AcademicYear,
) -> Optional[Stream]:
    """
    Recommends the least populated ACTIVE stream within a class level
    for a given academic year.
    """
    streams = (
        Stream.objects
        .filter(
            class_level=class_level,
            academic_year=academic_year,
            is_active=True,
        )
        .annotate(
            student_count=Count(
                'enrollments',
                filter=Q(enrollments__status='active')
            )
        )
        .order_by('student_count', 'order')
    )

    return streams.first()


def auto_assign_stream(
    student: Student,
    class_level: ClassLevel,
    academic_year: AcademicYear,
    assigned_by=None,
) -> Optional[StudentStreamEnrollment]:
    """
    Automatically assigns a student to the least populated stream.
    Creates a StudentStreamEnrollment record.
    """

    recommended_stream = recommend_least_populated_stream(
        class_level=class_level,
        academic_year=academic_year,
    )

    if not recommended_stream:
        return None

    enrollment, created = StudentStreamEnrollment.objects.get_or_create(
        student=student,
        academic_year=academic_year,
        defaults={
            'stream': recommended_stream,
            'status': 'active',
            'assigned_by': assigned_by,
        }
    )

    return enrollment


# ======================================================
# 🔹 CLASS LEVEL TRANSFER RECOMMENDATIONS
# ======================================================

def recommend_class_for_transfer(
    student: Student,
    current_class_level: ClassLevel,
) -> Optional[ClassLevel]:
    """
    Recommends a new class level for transfer or promotion.
    Placeholder logic – should later use analytics snapshots.
    """

    # Placeholder for ML / AI score
    performance_score = random.uniform(0, 1)

    if performance_score < 0.8:
        return None

    return (
        ClassLevel.objects
        .filter(
            institution=current_class_level.institution,
            order__gt=current_class_level.order
        )
        .order_by('order')
        .first()
    )


# ======================================================
# 🔹 CLASS / STREAM DISTRIBUTION REPORT
# ======================================================

def generate_class_distribution_report(
    institution_id: int,
    academic_year: AcademicYear,
) -> List[Dict]:
    """
    Generates student distribution across class levels and streams.
    Uses enrollment data (single source of truth).
    """

    report = []

    class_levels = (
        ClassLevel.objects
        .filter(institution_id=institution_id)
        .order_by('order')
    )

    for level in class_levels:
        streams = (
            Stream.objects
            .filter(
                class_level=level,
                academic_year=academic_year,
                is_active=True,
            )
            .annotate(
                student_count=Count(
                    'enrollments',
                    filter=Q(enrollments__status='active')
                )
            )
            .order_by('order')
        )

        stream_data = [
            {
                'stream': stream.name,
                'stream_code': stream.code,
                'students': stream.student_count,
                'capacity': stream.capacity,
            }
            for stream in streams
        ]

        report.append({
            'class_level': level.name,
            'class_level_code': level.code,
            'streams': stream_data,
            'total_students': sum(s['students'] for s in stream_data),
        })

    return report


# ======================================================
# 🔹 OVERCROWDING DETECTION
# ======================================================

def highlight_overcrowded_streams(
    institution_id: int,
    academic_year: AcademicYear,
) -> List[Stream]:
    """
    Returns streams where ACTIVE students exceed capacity.
    """

    return (
        Stream.objects
        .filter(
            academic_year=academic_year,
            class_level__institution_id=institution_id,
            is_active=True,
        )
        .annotate(
            student_count=Count(
                'enrollments',
                filter=Q(enrollments__status='active')
            )
        )
        .filter(student_count__gt=F('capacity'))
        .order_by('-student_count')
    )


# ======================================================
# 🔹 BALANCED ALLOCATION SUGGESTIONS
# ======================================================

def suggest_balanced_allocation(
    institution_id: int,
    academic_year: AcademicYear,
    imbalance_threshold: int = 10,
) -> List[Dict]:
    """
    Suggests redistribution plans within each class level
    to reduce overcrowding.
    """

    suggestions = []

    class_levels = ClassLevel.objects.filter(
        institution_id=institution_id
    )

    for level in class_levels:
        streams = (
            Stream.objects
            .filter(
                class_level=level,
                academic_year=academic_year,
                is_active=True,
            )
            .annotate(
                student_count=Count(
                    'enrollments',
                    filter=Q(enrollments__status='active')
                )
            )
            .order_by('student_count')
        )

        if streams.count() < 2:
            continue

        least = streams.first()
        most = streams.last()

        imbalance = most.student_count - least.student_count

        if imbalance >= imbalance_threshold:
            suggestions.append({
                'class_level': level.name,
                'from_stream': most.name,
                'to_stream': least.name,
                'students_to_move': imbalance // 2,
                'from_count': most.student_count,
                'to_count': least.student_count,
            })

    return suggestions


# ======================================================
# 🔹 AI INSIGHTS FROM ANALYTICS SNAPSHOTS
# ======================================================

def evaluate_stream_risk(
    stream_analytics: StreamAnalytics,
) -> str:
    """
    Simple AI evaluation using analytics snapshots.
    """

    if stream_analytics.average_score < 40:
        return 'High academic risk'

    if stream_analytics.attendance_rate < 75:
        return 'Attendance risk'

    if stream_analytics.discipline_index > 3:
        return 'Discipline risk'

    return 'Normal'
