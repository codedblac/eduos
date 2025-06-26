from .models import DisciplineCase
from django.utils.timezone import now, timedelta
from django.db.models import Count, Q
from students.models import Student


def detect_repeat_offenders(institution, threshold=3, days=30):
    """
    Returns students with ≥ `threshold` cases in the last `days` days.
    """
    since = now().date() - timedelta(days=days)
    cases = DisciplineCase.objects.filter(
        institution=institution,
        incident_date__gte=since
    ).values('student__id', 'student__user__first_name', 'student__user__last_name')\
     .annotate(count=Count('id'))\
     .filter(count__gte=threshold)\
     .order_by('-count')
    return cases


def flag_severe_recent_cases(institution, days=7):
    """
    Identify students with SEVERE cases filed in the last 7 days.
    """
    recent = now().date() - timedelta(days=days)
    return DisciplineCase.objects.filter(
        institution=institution,
        severity='severe',
        incident_date__gte=recent
    ).select_related('student')


def suggest_intervention(student_id, institution):
    """
    Suggests intervention strategies based on past behavior.
    """
    recent_cases = DisciplineCase.objects.filter(
        student__id=student_id,
        institution=institution
    ).order_by('-incident_date')[:5]

    suggestions = []
    severity_levels = [case.severity for case in recent_cases]

    if severity_levels.count('severe') >= 2:
        suggestions.append("Schedule meeting with parents & counselor.")
    if severity_levels.count('moderate') >= 3:
        suggestions.append("Place student under behavioral observation.")
    if len(recent_cases) >= 5:
        suggestions.append("Initiate mentorship or peer guidance.")

    return suggestions
