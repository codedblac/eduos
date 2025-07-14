# exams/analytics.py

from collections import defaultdict, Counter
from datetime import datetime
from django.db.models import Avg, Count, Max, Min, StdDev

from exams.models import (
    Exam, ExamSubject, StudentScore, ExamResult, ExamInsight
)
from students.models import Student
from subjects.models import Subject
from institutions.models import Institution


def overall_exam_performance(institution: Institution):
    """
    Returns average performance summary per subject across all exams.
    """
    return list(StudentScore.objects.filter(
        exam_subject__exam__institution=institution
    ).values('exam_subject__subject__name').annotate(
        avg_score=Avg('score'),
        max_score=Max('score'),
        min_score=Min('score'),
        std_dev=StdDev('score'),
        count=Count('id')
    ).order_by('-avg_score'))


def individual_student_report(student: Student):
    """
    Provides historical performance trend for a student across all exams.
    """
    results = ExamResult.objects.filter(student=student).order_by('exam__year', 'exam__term')
    return [
        {
            "exam": result.exam.name,
            "term": result.exam.term,
            "year": result.exam.year,
            "total_score": result.total_score,
            "average_score": result.average_score,
            "grade": result.grade,
        }
        for result in results
    ]


def subject_wise_performance(exam: Exam):
    """
    Get subject-level analytics for a specific exam.
    """
    return list(StudentScore.objects.filter(
        exam_subject__exam=exam
    ).values('exam_subject__subject__name').annotate(
        avg_score=Avg('score'),
        highest_score=Max('score'),
        lowest_score=Min('score'),
        most_common_grade=Max('grade'),  # Optional: update to most frequent
        count=Count('id')
    ))


def top_students_by_exam(exam: Exam, top_n: int = 10):
    """
    Return the top N students based on average score for a given exam.
    """
    return ExamResult.objects.filter(exam=exam).order_by('-average_score')[:top_n]


def underperforming_students(exam: Exam, threshold: float = 40.0):
    """
    Return students who scored below the average threshold.
    """
    return ExamResult.objects.filter(
        exam=exam,
        average_score__lt=threshold
    )


def grade_distribution_for_subject(exam_subject: ExamSubject):
    """
    Return grade counts for a single subject within an exam.
    """
    grades = StudentScore.objects.filter(exam_subject=exam_subject).values_list('grade', flat=True)
    return dict(Counter(grades))


def compute_insights_for_exam(exam: Exam):
    """
    Create or update insights per subject for an exam.
    """
    insights = []

    for exam_subject in exam.subjects.all():
        scores = StudentScore.objects.filter(exam_subject=exam_subject)

        if not scores.exists():
            continue

        grade_counts = Counter(scores.values_list('grade', flat=True))
        most_common_grade = grade_counts.most_common(1)[0][0] if grade_counts else "N/A"

        avg_score = scores.aggregate(avg=Avg('score'))['avg'] or 0
        high_score = scores.aggregate(high=Max('score'))['high'] or 0
        low_score = scores.aggregate(low=Min('score'))['low'] or 0

        summary = f"{most_common_grade} was most common. Avg: {avg_score:.2f}"

        insight, _ = ExamInsight.objects.update_or_create(
            exam=exam,
            subject=exam_subject.subject,
            defaults={
                'average_score': avg_score,
                'highest_score': high_score,
                'lowest_score': low_score,
                'most_common_grade': most_common_grade,
                'insight_summary': summary,
                'generated_at': datetime.now()
            }
        )
        insights.append(insight)

    return insights


def grade_heatmap_per_class_level(institution: Institution):
    """
    Grade distribution across class levels for heatmap analytics.
    """
    heatmap = defaultdict(lambda: defaultdict(int))

    data = StudentScore.objects.filter(
        exam_subject__exam__institution=institution
    ).values(
        'student__class_level__name', 'grade'
    ).annotate(count=Count('id'))

    for entry in data:
        level = entry['student__class_level__name']
        grade = entry['grade']
        heatmap[level][grade] += entry['count']

    return dict(heatmap)


def grade_gap_analysis(institution: Institution):
    """
    Identify subjects with wide performance gaps across class levels.
    """
    gaps = []

    for subject in Subject.objects.all():
        stats = StudentScore.objects.filter(
            exam_subject__subject=subject,
            exam_subject__exam__institution=institution
        ).values('student__class_level__name').annotate(avg_score=Avg('score'))

        scores = [row['avg_score'] for row in stats if row['avg_score'] is not None]

        if len(scores) > 1:
            gap = max(scores) - min(scores)
            if gap > 15:  # Significant disparity
                gaps.append({
                    'subject': subject.name,
                    'gap': round(gap, 2),
                    'levels': stats
                })

    return gaps
