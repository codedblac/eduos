from .models import ClassLevel, Stream
from students.models import Student
from django.db.models import Count
from typing import Optional, List, Dict
import random


def recommend_least_populated_stream(class_level: ClassLevel) -> Optional[Stream]:
    """
    Recommends the stream within the given class level that has the fewest students.
    """
    streams = class_level.streams.annotate(student_count=Count('students')).order_by('student_count')
    return streams.first() if streams.exists() else None


def auto_assign_stream(student: Student) -> Optional[Stream]:
    """
    Automatically assigns a student to the least populated stream in their class level.
    Returns the assigned stream or None.
    """
    if not student.class_level:
        return None

    recommended_stream = recommend_least_populated_stream(student.class_level)
    if recommended_stream:
        student.stream = recommended_stream
        student.save(update_fields = ['stream'])
        return recommended_stream
    return None


def recommend_class_for_transfer(student: Student) -> Optional[ClassLevel]:
    """
    Recommends a new class level for a student's transfer based on performance or age.
    (Stub logic, can be enhanced by integrating performance scores or AI model.)
    """
    # Placeholder logic simulating performance-based recommendation
    performance_score = random.uniform(0, 1)  # Replace with real evaluation later
    if performance_score > 0.8 and student.class_level:
        next_level = (
            ClassLevel.objects.filter(
                institution=student.institution,
                order__gt=student.class_level.order
            ).order_by('order').first()
        )
        return next_level
    return None


def generate_class_distribution_report(institution) -> List[Dict]:
    """
    Generates a structured report of student distribution across all class levels and streams.
    Useful for visualizations, dashboards, and audits.
    """
    report = []
    class_levels = ClassLevel.objects.filter(institution=institution).order_by('order')

    for level in class_levels:
        streams = level.streams.annotate(student_count=Count('students')).order_by('order')
        stream_data = [
            {
                'stream': stream.name,
                'stream_code': stream.code,
                'students': stream.student_count
            }
            for stream in streams
        ]

        level_summary = {
            'class_level': level.name,
            'class_level_code': level.code,
            'streams': stream_data,
            'total_students': sum(s['students'] for s in stream_data)
        }
        report.append(level_summary)

    return report


def highlight_overcrowded_streams(threshold: int = 45) -> List[Stream]:
    """
    Returns a queryset of streams with student count above a defined overcrowding threshold.
    Default threshold: 45 students per stream.
    """
    return Stream.objects.annotate(student_count=Count('students')).filter(student_count__gt=threshold)


def suggest_balanced_allocation(institution) -> List[Dict]:
    """
    Suggests a redistribution plan for overloaded and underloaded streams within each class level.
    Can be used by admin to manually move students and reduce crowding.
    """
    suggestions = []
    class_levels = ClassLevel.objects.filter(institution=institution)

    for level in class_levels:
        streams = level.streams.annotate(student_count=Count('students')).order_by('student_count')

        if streams.count() < 2:
            continue  # Need at least 2 streams to balance

        most = streams.last()
        least = streams.first()
        imbalance = most.student_count - least.student_count

        if imbalance >= 10:
            suggestions.append({
                'class_level': level.name,
                'from_stream': most.name,
                'to_stream': least.name,
                'students_to_move': imbalance // 2,
                'from_count': most.student_count,
                'to_count': least.student_count
            })

    return suggestions
