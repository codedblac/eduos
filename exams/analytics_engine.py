# exams/analytics_engine.py

from django.db.models import Avg, Count, Max, Min, Sum
from .models import ExamResult
from subjects.models import Subject
from accounts.models import Student
from classes.models import Stream, ClassLevel

def get_student_performance_summary(student_id):
    """
    Returns average score, total marks, grade summary for a single student across all exams.
    """
    results = ExamResult.objects.filter(student_id=student_id)
    if not results.exists():
        return None

    total_marks = results.aggregate(Sum('marks'))['marks__sum']
    average_score = results.aggregate(Avg('marks'))['marks__avg']
    subject_count = results.count()

    grade_summary = results.values('grade').annotate(count=Count('grade'))

    return {
        "student_id": student_id,
        "average_score": round(average_score, 2),
        "total_marks": total_marks,
        "subjects_taken": subject_count,
        "grade_summary": list(grade_summary)
    }

def get_subject_performance(exam_id):
    """
    Returns average, max, and min scores per subject in a given exam.
    """
    subjects = Subject.objects.all()
    analytics = []

    for subject in subjects:
        results = ExamResult.objects.filter(exam_id=exam_id, subject=subject)
        if not results.exists():
            continue

        stats = results.aggregate(
            avg_score=Avg('marks'),
            max_score=Max('marks'),
            min_score=Min('marks'),
            entries=Count('id')
        )

        analytics.append({
            "subject": subject.name,
            "average_score": round(stats['avg_score'], 2),
            "max_score": stats['max_score'],
            "min_score": stats['min_score'],
            "entries": stats['entries']
        })

    return analytics

def get_stream_ranking(exam_id, stream_id):
    """
    Ranks students in a stream based on their total marks in a given exam.
    """
    results = ExamResult.objects.filter(exam_id=exam_id, stream_id=stream_id)
    if not results.exists():
        return []

    student_scores = {}

    for result in results:
        student_id = result.student_id
        student_scores[student_id] = student_scores.get(student_id, 0) + result.marks

    ranked = sorted(student_scores.items(), key=lambda x: x[1], reverse=True)

    return [
        {
            "rank": idx + 1,
            "student_id": student_id,
            "total_marks": total_marks
        }
        for idx, (student_id, total_marks) in enumerate(ranked)
    ]

def get_class_level_summary(exam_id, class_level_id):
    """
    Summarizes overall class performance in a given exam.
    """
    results = ExamResult.objects.filter(exam_id=exam_id, exam__class_level_id=class_level_id)

    if not results.exists():
        return {}

    avg_score = results.aggregate(Avg('marks'))['marks__avg']
    top_student = results.values('student').annotate(total=Sum('marks')).order_by('-total').first()

    return {
        "average_score": round(avg_score, 2),
        "top_student_id": top_student['student'] if top_student else None,
        "top_total_score": top_student['total'] if top_student else None
    }
