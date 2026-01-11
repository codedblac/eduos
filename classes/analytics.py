# classes/analytics.py

from django.db.models import Count, Q
from academics.models import AcademicYear
from .models import ClassLevel, Stream, StudentStreamEnrollment

# ======================================================
# Helper to get current academic year if not provided
# ======================================================
def get_academic_year_id(institution_id, academic_year_id=None):
    if academic_year_id is not None:
        return academic_year_id
    academic_year = (
        AcademicYear.objects
        .filter(institution_id=institution_id, is_current=True)
        .first()
    )
    if not academic_year:
        raise ValueError("No active academic year found for this institution")
    return academic_year.id


# ======================================================
# CLASS LEVEL DISTRIBUTION
# ======================================================
def get_class_level_distribution(institution_id, academic_year_id=None):
    academic_year_id = get_academic_year_id(institution_id, academic_year_id)
    
    class_levels = (
        ClassLevel.objects.filter(institution_id=institution_id)
        .annotate(
            total_students=Count(
                'streams__enrollments',
                filter=Q(
                    streams__enrollments__status='active',
                    streams__academic_year_id=academic_year_id
                )
            )
        )
        .order_by('order', 'name')
    )

    return [
        {
            "id": cl.id,
            "name": cl.name,
            "total_students": cl.total_students
        }
        for cl in class_levels
    ]


# ======================================================
# STREAM DISTRIBUTION
# ======================================================
def get_stream_distribution(institution_id, academic_year_id=None):
    academic_year_id = get_academic_year_id(institution_id, academic_year_id)
    
    streams = Stream.objects.filter(
        class_level__institution_id=institution_id,
        academic_year_id=academic_year_id
    ).annotate(
        total_students=Count('enrollments', filter=Q(enrollments__status='active'))
    )

    return [
        {
            "id": s.id,
            "name": s.name,
            "class_level_id": s.class_level_id,
            "total_students": s.total_students
        }
        for s in streams
    ]


# ======================================================
# GENDER BREAKDOWN PER CLASS
# ======================================================
def get_gender_breakdown_per_class(institution_id, academic_year_id=None):
    academic_year_id = get_academic_year_id(institution_id, academic_year_id)
    
    class_levels = ClassLevel.objects.filter(institution_id=institution_id)
    result = []
    for cl in class_levels:
        male_count = StudentStreamEnrollment.objects.filter(
            stream__class_level=cl,
            stream__academic_year_id=academic_year_id,
            status='active',
            student__gender='male'
        ).count()
        female_count = StudentStreamEnrollment.objects.filter(
            stream__class_level=cl,
            stream__academic_year_id=academic_year_id,
            status='active',
            student__gender='female'
        ).count()
        result.append({
            "class_level_id": cl.id,
            "male": male_count,
            "female": female_count
        })
    return result


# ======================================================
# OVERCROWDED STREAMS
# ======================================================
def get_overcrowded_streams(institution_id, academic_year_id=None, threshold=40):
    academic_year_id = get_academic_year_id(institution_id, academic_year_id)
    
    streams = Stream.objects.filter(
        class_level__institution_id=institution_id,
        academic_year_id=academic_year_id
    ).annotate(
        total_students=Count('enrollments', filter=Q(enrollments__status='active'))
    )
    return [
        {
            "id": s.id,
            "name": s.name,
            "total_students": s.total_students
        }
        for s in streams if s.total_students > threshold
    ]


# ======================================================
# EMPTY CLASSES AND STREAMS
# ======================================================
def get_empty_classes_and_streams(institution_id, academic_year_id=None):
    academic_year_id = get_academic_year_id(institution_id, academic_year_id)
    
    empty_classes = ClassLevel.objects.filter(
        institution_id=institution_id,
        streams__academic_year_id=academic_year_id
    ).annotate(
        total_students=Count(
            'streams__enrollments',
            filter=Q(
                streams__enrollments__status='active',
                streams__academic_year_id=academic_year_id
            )
        )
    ).filter(total_students=0)

    empty_streams = Stream.objects.filter(
        class_level__institution_id=institution_id,
        academic_year_id=academic_year_id
    ).annotate(
        total_students=Count('enrollments', filter=Q(enrollments__status='active'))
    ).filter(total_students=0)

    return {
        "empty_classes": [{"id": cl.id, "name": cl.name} for cl in empty_classes],
        "empty_streams": [{"id": s.id, "name": s.name} for s in empty_streams],
    }


# ======================================================
# ENROLLMENT STATUS STATS
# ======================================================
def get_enrollment_status_stats(institution_id, academic_year_id=None):
    academic_year_id = get_academic_year_id(institution_id, academic_year_id)
    
    streams = Stream.objects.filter(
        class_level__institution_id=institution_id,
        academic_year_id=academic_year_id
    )
    total_enrolled = StudentStreamEnrollment.objects.filter(
        stream__in=streams, status='active'
    ).count()
    total_pending = StudentStreamEnrollment.objects.filter(
        stream__in=streams, status='pending'
    ).count()

    return {
        "active": total_enrolled,
        "pending": total_pending
    }


# ======================================================
# TOTAL SUMMARY
# ======================================================
def get_total_summary(institution_id, academic_year_id=None):
    academic_year_id = get_academic_year_id(institution_id, academic_year_id)
    
    total_classes = ClassLevel.objects.filter(institution_id=institution_id).count()
    total_streams = Stream.objects.filter(
        class_level__institution_id=institution_id,
        academic_year_id=academic_year_id
    ).count()
    total_students = StudentStreamEnrollment.objects.filter(
        stream__class_level__institution_id=institution_id,
        stream__academic_year_id=academic_year_id,
        status='active'
    ).count()

    return {
        "classes": total_classes,
        "streams": total_streams,
        "students": total_students
    }
