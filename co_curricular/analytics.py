from collections import defaultdict
from django.db.models import Count, Q
from students.models import Student
from .models import (
    StudentProfile,
    StudentActivityParticipation,
    Activity,
    StudentAward,
)


def get_participation_summary(institution=None):
    """
    Returns summary of student participation in co-curricular activities.
    """
    queryset = StudentActivityParticipation.objects.select_related('student', 'activity')
    if institution:
        queryset = queryset.filter(student__institution=institution)

    total = queryset.count()
    by_activity = queryset.values('activity__name').annotate(count=Count('id'))
    by_gender = queryset.values('student__gender').annotate(count=Count('id'))
    by_class = queryset.values('student__current_class__name').annotate(count=Count('id'))

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
    return StudentAward.objects.values(
        'activity__name', 'level', 'term__name'
    ).annotate(count=Count('id')).order_by('activity__name', 'term__name')


def get_student_talent_distribution():
    """
    Returns number of activities per student profile.
    """
    return StudentProfile.objects.annotate(
        total_activities=Count('participations')
    ).values('student__full_name', 'total_activities')


def get_activity_popularity():
    """
    Lists most popular activities by student participation.
    """
    return Activity.objects.annotate(
        participation_count=Count('studentactivityparticipation')
    ).order_by('-participation_count')[:10]


def detect_low_participation_students(threshold=1):
    """
    Return list of students with fewer than `threshold` participations.
    """
    return Student.objects.annotate(
        activity_count=Count('studentactivityparticipation')
    ).filter(activity_count__lt=threshold)


def detect_gender_disparity_by_activity():
    """
    Analyze gender distribution per activity.
    """
    result = defaultdict(lambda: {'male': 0, 'female': 0, 'other': 0})
    participations = StudentActivityParticipation.objects.select_related('student', 'activity')

    for p in participations:
        gender = (p.student.gender or 'other').lower()
        result[p.activity.name][gender] += 1

    return result


def activity_trends_over_time():
    """
    Participation trends by activity and term.
    """
    return StudentActivityParticipation.objects.values(
        'activity__name', 'term__name'
    ).annotate(count=Count('id')).order_by('activity__name', 'term__start_date')


def coach_performance_summary():
    """
    Summary of coach impact based on awards.
    """
    return StudentAward.objects.values('awarded_by__full_name').annotate(
        total_awards=Count('id'),
        unique_activities=Count('activity', distinct=True)
    ).order_by('-total_awards')
