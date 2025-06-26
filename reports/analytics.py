from .models import ReportStudentPerformance, ReportSubjectBreakdown
from django.db.models import Avg, Count, Q, Max, Min


def class_average_per_term(institution, class_level, stream):
    return ReportStudentPerformance.objects.filter(
        report__institution=institution,
        class_level=class_level,
        stream=stream
    ).values('report__term', 'report__year').annotate(
        mean_score=Avg('mean_score'),
        average_grade=Avg('mean_score'),
        student_count=Count('id')
    ).order_by('report__year', 'report__term')


def subject_difficulty_index(institution, class_level=None):
    """
    Subjects with lowest average scores → harder subjects.
    """
    qs = ReportSubjectBreakdown.objects.filter(report__institution=institution)
    if class_level:
        qs = qs.filter(class_level=class_level)

    return qs.values('subject__name').annotate(
        avg_score=Avg('average_score'),
        pass_rate=Avg('pass_rate'),
        fail_rate=Avg('failure_rate'),
        report_count=Count('id')
    ).order_by('avg_score')


def stream_top_performers(report, top_n=5):
    return ReportStudentPerformance.objects.filter(
        report=report
    ).order_by('-mean_score')[:top_n]


def grade_distribution_chart(report):
    """
    Returns a dictionary: {grade: count}
    """
    data = ReportStudentPerformance.objects.filter(report=report).values('grade').annotate(count=Count('id'))
    return {entry['grade']: entry['count'] for entry in data}


def most_improved_students(institution, student_ids):
    """
    Compares latest two reports to identify improvements.
    """
    improvements = []
    for student_id in student_ids:
        perfs = ReportStudentPerformance.objects.filter(student__id=student_id).order_by('-report__year', '-report__term')[:2]
        if len(perfs) == 2:
            diff = perfs[0].mean_score - perfs[1].mean_score
            if diff > 0:
                improvements.append({
                    "student_id": student_id,
                    "improvement": diff
                })
    return sorted(improvements, key=lambda x: x["improvement"], reverse=True)
