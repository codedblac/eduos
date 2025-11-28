# exams/utils.py

from typing import Dict, List, Optional
from collections import defaultdict
from django.db.models import Avg, Max, Min, Count

from django.utils.text import slugify
from exams.models import StudentScore, ExamResult, GradeBoundary, Exam, ExamSubject
from students.models import Student
from institutions.models import Institution


def get_grade_from_score(score: Optional[float], subject, institution: Institution) -> str:
    """
    Convert numeric score into a grade based on grade boundaries for an institution.
    """
    if score is None:
        return "N/A"

    boundaries = GradeBoundary.objects.filter(
        institution=institution,
        subject=subject
    ).order_by('-min_score')

    for boundary in boundaries:
        if boundary.min_score <= score <= boundary.max_score:
            return boundary.grade

    return "E"  # Default fallback


def calculate_position(scores_queryset) -> Dict[int, int]:
    """
    Assign ranking positions based on descending scores.
    Returns: {student_id: position}
    """
    scores = list(scores_queryset.order_by('-score').values('student_id', 'score'))
    position_map = {}
    current_position = 1
    prev_score = None
    tied_count = 0

    for index, item in enumerate(scores):
        if item['score'] != prev_score:
            current_position += tied_count
            tied_count = 1
        else:
            tied_count += 1
        prev_score = item['score']
        position_map[item['student_id']] = current_position

    return position_map


def calculate_exam_statistics(exam: Exam) -> dict:
    """
    Calculate aggregate statistics for an exam.
    """
    scores = StudentScore.objects.filter(exam_subject__exam=exam)

    if not scores.exists():
        return {
            'average': 0.0,
            'max': 0.0,
            'min': 0.0,
            'most_common_grade': 'N/A'
        }

    aggregate_data = scores.aggregate(
        avg=Avg('score'),
        high=Max('score'),
        low=Min('score')
    )

    grade_counts = scores.values('grade').annotate(count=Count('grade')).order_by('-count')
    most_common_grade = grade_counts[0]['grade'] if grade_counts else 'N/A'

    return {
        'average': round(aggregate_data['avg'], 2),
        'max': aggregate_data['high'],
        'min': aggregate_data['low'],
        'most_common_grade': most_common_grade
    }


def bulk_assign_grades_and_positions(exam: Exam):
    """
    Assign grades and positions to all student scores for each subject in the exam.
    """
    subjects = exam.subjects.all()
    institution = exam.institution

    for exam_subject in ExamSubject.objects.filter(exam=exam, subject__in=subjects).select_related('subject'):
        scores = StudentScore.objects.filter(exam_subject=exam_subject)
        grade_map = {
            score.id: get_grade_from_score(score.score, exam_subject.subject, institution)
            for score in scores
        }

        StudentScore.objects.bulk_update(
            [StudentScore(id=pk, grade=grade) for pk, grade in grade_map.items()],
            ['grade']
        )

        # Calculate and update positions
        position_map = calculate_position(scores)
        StudentScore.objects.bulk_update(
            [StudentScore(id=score.id, position=position_map.get(score.student_id)) for score in scores],
            ['position']
        )


def normalize_score(raw_score: float, max_raw: float, target_max: int = 100) -> float:
    """
    Normalize a raw score to a scale out of target_max (e.g., 100).
    """
    if max_raw == 0:
        return 0.0
    return round((raw_score / max_raw) * target_max, 2)


def get_student_exam_summary(student: Student, exam: Exam) -> dict:
    """
    Get detailed summary for a student's performance in an exam.
    """
    scores = StudentScore.objects.filter(
        student=student,
        exam_subject__exam=exam
    ).select_related('exam_subject__subject')

    total_score = 0
    subjects = []

    for score in scores:
        subjects.append({
            "subject": score.exam_subject.subject.name,
            "score": score.score,
            "grade": score.grade,
            "position": score.position
        })
        total_score += score.score or 0

    average = round(total_score / scores.count(), 2) if scores.exists() else 0

    return {
        "student": student.user.get_full_name(),
        "exam": str(exam),
        "total_score": total_score,
        "average_score": average,
        "subjects": subjects
    }


def generate_student_ranking(exam: Exam):
    """
    Rank students by average score and store in ExamResult.
    """
    results = ExamResult.objects.filter(exam=exam).order_by('-average_score')

    rank = 1
    prev_score = None
    tied = 0

    for result in results:
        if result.average_score != prev_score:
            rank += tied
            tied = 1
        else:
            tied += 1
        prev_score = result.average_score
        result.overall_position = rank
        result.save(update_fields = ['overall_position'])


def generate_exam_slug(name: str, year: int = None, term: str = None) -> str:
    """
    Generates a unique slug for an exam using its name, year, and term.

    Example output: 'math-exam-term-1-2025'
    """
    base = slugify(name)
    parts = [base]
    if term:
        parts.append(slugify(term))
    if year:
        parts.append(str(year))
    return '-'.join(parts)

def format_exam_label(subject: str, class_level: str, term: str, year: int) -> str:
    """
    Formats a human-readable exam label like:
    'Mathematics - Grade 6 - Term 1 - 2025'
    """
    return f"{subject} - {class_level} - {term} - {year}"