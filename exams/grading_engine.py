# exams/grading_engine.py

from .models import Exam, ExamResult
from typing import Optional, List

# Grade boundaries — editable per country/level
GRADE_BOUNDARIES = {
    'A': 80,
    'A-': 75,
    'B+': 70,
    'B': 65,
    'B-': 60,
    'C+': 55,
    'C': 50,
    'C-': 45,
    'D+': 40,
    'D': 35,
    'E': 0,
}

def get_grade_from_marks(marks: Optional[float]) -> str:
    """
    Convert numeric marks to a grade using CBC boundaries.
    Returns 'N/A' if marks is None.
    """
    if marks is None:
        return "N/A"

    for grade, boundary in sorted(GRADE_BOUNDARIES.items(), key=lambda x: -x[1]):
        if marks >= boundary:
            return grade
    return "E"  # Fallback


def grade_exam_result(result: ExamResult):
    """
    Grade a single ExamResult instance.
    """
    result.grade = get_grade_from_marks(result.marks)
    result.save(update_fields=["grade"])


def grade_all_results_for_exam(exam: Exam):
    """
    Grade all ExamResults for a given Exam.
    """
    results = ExamResult.objects.filter(exam=exam)
    for result in results:
        if result.marks is not None:
            result.grade = get_grade_from_marks(result.marks)
            result.save(update_fields=["grade"])


def bulk_grade_results(results: List[ExamResult]):
    """
    Grade a list of ExamResults (e.g., from a queryset or filtered batch).
    """
    for result in results:
        if result.marks is not None:
            result.grade = get_grade_from_marks(result.marks)
            result.save(update_fields=["grade"])
