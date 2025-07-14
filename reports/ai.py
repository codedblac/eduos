from .models import ReportStudentPerformance, ReportSubjectBreakdown
from django.db.models import Q, Count, Avg
from django.utils.timezone import now


def detect_at_risk_students(report, critical_threshold=40.0):
    """
    Detect students whose mean_score falls below the critical threshold.
    """
    return ReportStudentPerformance.objects.filter(
        report=report,
        mean_score__lt=critical_threshold
    )


def categorize_students(report):
    """
    Classify students into performance tiers:
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

    performances = ReportStudentPerformance.objects.filter(report=report)

    for perf in performances:
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


def generate_summary_for_student(perf):
    """
    Return a personalized academic performance summary string for a student.
    """
    score = perf.mean_score
    name = perf.student.full_name

    if score >= 80:
        return f"{name} has demonstrated outstanding academic performance with a mean score of {score:.1f}."
    elif score >= 60:
        return f"{name} is performing well overall with a solid mean score of {score:.1f}."
    elif score >= 40:
        return f"{name} is showing average academic progress with a mean score of {score:.1f}."
    else:
        return f"{name} is at academic risk with a mean score of {score:.1f}. Immediate intervention is recommended."


def suggest_actions_for_student(perf):
    """
    Suggest tailored academic interventions for a student.
    """
    score = perf.mean_score

    if score >= 80:
        return "Maintain current study habits. Consider peer tutoring or mentorship roles."
    elif score >= 60:
        return "Encourage continued effort. Offer optional enrichment materials."
    elif score >= 40:
        return "Provide structured revision plans and weekly monitoring of weak subjects."
    else:
        return "Flag as high-risk. Recommend remedial classes, parental engagement, and academic counseling."


def subject_failure_alerts(report, threshold=50.0):
    """
    Identify subjects in a report with failure rates exceeding a given threshold.
    """
    alerts = []

    for breakdown in report.subject_breakdowns.all():
        if breakdown.failure_rate > threshold:
            alerts.append({
                'subject': breakdown.subject.name,
                'failure_rate': round(breakdown.failure_rate, 1),
                'average_score': round(breakdown.average_score, 1),
                'class_level': breakdown.class_level.name if breakdown.class_level else "",
                'stream': breakdown.stream.name if breakdown.stream else "",
            })

    return alerts


def teacher_impact_estimation(institution, class_level=None, stream=None):
    """
    Estimate average subject performance per teacher in a given institution.
    Returns a list sorted by average score.
    """
    queryset = ReportSubjectBreakdown.objects.filter(report__institution=institution)

    if class_level:
        queryset = queryset.filter(class_level=class_level)
    if stream:
        queryset = queryset.filter(stream=stream)

    return queryset.values(
        'teacher__id',
        'teacher__first_name',
        'teacher__last_name'
    ).annotate(
        subject_count=Count('id'),
        avg_score=Avg('average_score')
    ).order_by('-avg_score')


def generate_smart_comments_for_report(report):
    """
    Produce a high-level summary for the entire report using AI-style tone.
    Returns a dictionary with performance insights.
    """
    perf_qs = ReportStudentPerformance.objects.filter(report=report)
    avg_score = perf_qs.aggregate(avg=Avg('mean_score'))['avg'] or 0
    total_students = perf_qs.count()
    at_risk_count = perf_qs.filter(mean_score__lt=40).count()

    if avg_score >= 75:
        summary = "Overall academic performance is excellent."
    elif avg_score >= 60:
        summary = "The institution has shown solid academic progress."
    elif avg_score >= 40:
        summary = "Academic performance is moderate. Room for improvement exists."
    else:
        summary = "Academic interventions are urgently needed."

    return {
        "average_mean_score": round(avg_score, 2),
        "total_students": total_students,
        "students_at_risk": at_risk_count,
        "summary": summary
    }


def recommend_subject_interventions(report, low_pass_threshold=50):
    """
    Suggest interventions for subjects performing poorly.
    """
    recommendations = []

    for subject in report.subject_breakdowns.all():
        if subject.pass_rate < low_pass_threshold:
            recommendations.append({
                "subject": subject.subject.name,
                "issue": f"Low pass rate: {subject.pass_rate:.1f}%",
                "action": (
                    "Review teaching methods. Implement supplementary revision sessions, "
                    "peer assistance programs, or topic-specific re-teaching."
                )
            })

    return recommendations


def detect_improving_students(current_report, previous_report):
    """
    Detect students whose mean scores have improved compared to the previous report.
    Returns a list of improvement records.
    """
    current_data = {p.student_id: p for p in ReportStudentPerformance.objects.filter(report=current_report)}
    previous_data = {p.student_id: p for p in ReportStudentPerformance.objects.filter(report=previous_report)}

    improvements = []

    for student_id, current in current_data.items():
        prev = previous_data.get(student_id)
        if prev and current.mean_score > prev.mean_score:
            improvements.append({
                "student_id": student_id,
                "student_name": current.student.full_name,
                "previous_score": round(prev.mean_score, 2),
                "current_score": round(current.mean_score, 2),
                "improvement": round(current.mean_score - prev.mean_score, 2)
            })

    return sorted(improvements, key=lambda x: x['improvement'], reverse=True)
