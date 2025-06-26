from .models import ReportStudentPerformance, ReportSubjectBreakdown
from django.db.models import Q
from django.db.models import Count, Avg


def detect_at_risk_students(report, critical_threshold=40.0):
    """
    Returns all students below the critical threshold.
    """
    return ReportStudentPerformance.objects.filter(
        report=report,
        mean_score__lt=critical_threshold
    )


def categorize_students(report):
    """
    Classifies students into performance tiers:
    - Excellent (>= 80)
    - Good (60–79)
    - Average (40–59)
    - Weak (< 40)
    """
    tiers = {
        'excellent': [],
        'good': [],
        'average': [],
        'weak': [],
    }

    for perf in ReportStudentPerformance.objects.filter(report=report):
        score = perf.mean_score
        if score >= 80:
            tiers['excellent'].append(perf)
        elif score >= 60:
            tiers['good'].append(perf)
        elif score >= 40:
            tiers['average'].append(perf)
        else:
            tiers['weak'].append(perf)

    return tiers


def suggest_actions_for_student(perf):
    """
    AI-based academic intervention suggestions.
    """
    if perf.mean_score >= 80:
        return "Maintain current study habits. Consider academic mentorship roles."
    elif perf.mean_score >= 60:
        return "Encourage continued effort. Introduce light enrichment activities."
    elif perf.mean_score >= 40:
        return "Recommend targeted support. Review weak subject areas."
    else:
        return "Flag as at-risk. Initiate parental involvement, remedial classes, and counseling."


def subject_failure_alerts(report, threshold=50.0):
    """
    Returns list of subjects with high failure rates (> threshold).
    """
    alerts = []
    for sub in report.subject_breakdowns.all():
        if sub.failure_rate > threshold:
            alerts.append({
                'subject': sub.subject.name,
                'failure_rate': sub.failure_rate,
                'average_score': sub.average_score
            })
    return alerts


def teacher_impact_estimation(institution, class_level):
    """
    Estimates average score under each teacher.
    """
    qs = ReportSubjectBreakdown.objects.filter(report__institution=institution, class_level=class_level)
    return qs.values('teacher__first_name', 'teacher__last_name').annotate(
        subject_count=Count('id'),
        avg_score=Avg('average_score')
    ).order_by('-avg_score')
