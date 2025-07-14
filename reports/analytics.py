from django.db.models import Avg, Count, Q, Max, Min
from collections import defaultdict
from .models import ReportStudentPerformance, ReportSubjectBreakdown
from students.models import Student


def class_average_per_term(institution, class_level, stream=None):
    """
    Returns average student scores per term for a specific class and optional stream.
    """
    qs = ReportStudentPerformance.objects.filter(
        report__institution=institution,
        class_level=class_level,
    )

    if stream:
        qs = qs.filter(stream=stream)

    return qs.values('report__term', 'report__year').annotate(
        mean_score=Avg('mean_score'),
        average_grade=Avg('mean_score'),  # Alias for frontend mapping
        student_count=Count('id')
    ).order_by('report__year', 'report__term')


def subject_difficulty_index(institution, class_level=None, stream=None, limit=None):
    """
    Ranks subjects based on average scores (hardest = lowest score).
    """
    qs = ReportSubjectBreakdown.objects.filter(report__institution=institution)

    if class_level:
        qs = qs.filter(class_level=class_level)
    if stream:
        qs = qs.filter(stream=stream)

    result = qs.values(
        'subject__id',
        'subject__name'
    ).annotate(
        avg_score=Avg('average_score'),
        pass_rate=Avg('pass_rate'),
        fail_rate=Avg('failure_rate'),
        report_count=Count('id')
    ).order_by('avg_score')  # Ascending = harder

    return result[:limit] if limit else result


def stream_top_performers(report, top_n=5):
    """
    Returns top N students by mean_score for a specific report.
    """
    return ReportStudentPerformance.objects.filter(
        report=report
    ).select_related('student').order_by('-mean_score')[:top_n]


def grade_distribution_chart(report):
    """
    Returns distribution of grades in a given report.
    Output: {'A': {'count': 5, 'percent': 10.0}, ...}
    """
    qs = ReportStudentPerformance.objects.filter(report=report)
    total = qs.count()
    raw = qs.values('grade').annotate(count=Count('id'))

    return {
        entry['grade']: {
            'count': entry['count'],
            'percent': round(entry['count'] * 100 / total, 2) if total else 0.0
        }
        for entry in raw
    }


def most_improved_students(institution, student_ids=None, top_n=10):
    """
    Detect students with highest improvement in mean_score over last two reports.
    """
    improvements = []

    students_qs = Student.objects.filter(institution=institution)
    if student_ids:
        students_qs = students_qs.filter(id__in=student_ids)

    for student in students_qs.only('id', 'full_name'):
        perfs = ReportStudentPerformance.objects.filter(
            student=student
        ).order_by('-report__year', '-report__term')[:2]

        if len(perfs) == 2:
            latest, previous = perfs[0], perfs[1]
            delta = latest.mean_score - previous.mean_score
            if delta > 0:
                improvements.append({
                    "student_id": student.id,
                    "student_name": student.full_name,
                    "previous_score": round(previous.mean_score, 2),
                    "current_score": round(latest.mean_score, 2),
                    "improvement": round(delta, 2),
                    "class_level": str(latest.class_level),
                    "stream": str(latest.stream),
                })

    return sorted(improvements, key=lambda x: x['improvement'], reverse=True)[:top_n]


def subject_performance_trends(institution, subject, class_level=None):
    """
    Returns average score, top score, and pass rate per term for a given subject.
    """
    qs = ReportSubjectBreakdown.objects.filter(
        report__institution=institution,
        subject=subject
    )

    if class_level:
        qs = qs.filter(class_level=class_level)

    return qs.values('report__term', 'report__year').annotate(
        avg_score=Avg('average_score'),
        top_score=Max('top_score'),
        pass_rate=Avg('pass_rate')
    ).order_by('report__year', 'report__term')


def performance_heatmap(institution, year, term=None):
    """
    Generates heatmap data showing stream x subject average scores.
    Output: {stream: {subject: avg_score}}
    """
    qs = ReportSubjectBreakdown.objects.filter(
        report__institution=institution,
        report__year=year
    )

    if term:
        qs = qs.filter(report__term=term)

    heatmap = defaultdict(dict)

    for entry in qs.select_related('subject', 'stream'):
        subject = entry.subject.name
        stream = entry.stream.name if entry.stream else "Unknown"
        heatmap[stream][subject] = round(entry.average_score, 2)

    return dict(heatmap)


def report_summary(institution, year, term):
    """
    Summarizes academic performance for a term:
    - Mean score
    - Total students
    - Fails
    - Pass rate
    """
    qs = ReportStudentPerformance.objects.filter(
        report__institution=institution,
        report__year=year,
        report__term=term
    )

    total = qs.count()
    mean = qs.aggregate(avg=Avg('mean_score'))['avg'] or 0.0
    fails = qs.filter(mean_score__lt=40).count()

    return {
        "institution_id": institution.id,
        "year": year,
        "term": term,
        "average_mean_score": round(mean, 2),
        "total_students": total,
        "students_below_pass": fails,
        "pass_rate": round((total - fails) * 100 / total, 2) if total else 0.0
    }
