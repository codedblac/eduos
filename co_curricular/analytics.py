from collections import defaultdict
from django.db.models import Count, Avg, Q
from students.models import Student
from .models import (
    TalentProfile,
    StudentActivityParticipation,
    CoCurricularActivity,
    TalentAward,
)


def get_participation_summary(institution=None):
    """
    Returns summary of student participation in co-curricular activities.
    """
    queryset = StudentActivityParticipation.objects.all()
    if institution:
        queryset = queryset.filter(student__institution=institution)

    total = queryset.count()
    by_activity = queryset.values('activity__name').annotate(count=Count('id'))
    by_gender = queryset.values('student__gender').annotate(count=Count('id'))
    by_class = queryset.values('student__class_level__name').annotate(count=Count('id'))

    return {
        'total_participation': total,
        'by_activity': list(by_activity),
        'by_gender': list(by_gender),
        'by_class': list(by_class),
    }


def get_award_statistics():
    """
    Returns number of awards per activity, level, and term.
    """
    awards = TalentAward.objects.values(
        'activity__name', 'level', 'term__name'
    ).annotate(count=Count('id'))
    return list(awards)


def get_student_talent_distribution():
    """
    Returns how many talents are registered per student.
    """
    return TalentProfile.objects.values('student__full_name').annotate(
        total_talents=Count('talents')
    )


def get_activity_popularity():
    """
    Lists most popular activities by student participation.
    """
    return CoCurricularActivity.objects.annotate(
        participation_count=Count('participations')
    ).order_by('-participation_count')[:10]


def detect_low_participation_students(threshold=1):
    """
    Return list of students with fewer than `threshold` participations.
    """
    return Student.objects.annotate(
        activity_count=Count('participations')
    ).filter(activity_count__lt=threshold)


def detect_gender_disparity_by_activity():
    """
    Analyze gender balance in each activity.
    """
    result = defaultdict(lambda: {'male': 0, 'female': 0})
    participations = StudentActivityParticipation.objects.select_related('activity', 'student')

    for p in participations:
        gender = p.student.gender.lower()
        result[p.activity.name][gender] += 1

    return result


def activity_trends_over_time():
    """
    Detect participation patterns over terms/years.
    """
    trends = StudentActivityParticipation.objects.values(
        'activity__name', 'term__name'
    ).annotate(count=Count('id')).order_by('activity__name', 'term__start_date')

    return list(trends)


def coach_performance_summary():
    """
    Summary of coaches' engagements and awards.
    """
    return TalentAward.objects.values('awarded_by__full_name').annotate(
        total_awards=Count('id'),
        unique_activities=Count('activity', distinct=True)
    ).order_by('-total_awards')
