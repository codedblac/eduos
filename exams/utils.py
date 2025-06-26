# exams/utils.py

from collections import defaultdict
from django.db.models import F, Sum, Avg, Count
from .models import ExamResult, Exam
from students.models import Student
import random

# CBC-aligned grade boundaries (editable as needed)
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


def calculate_grade(marks: float) -> str:
    """
    Return the corresponding grade for given marks.
    """
    for grade, boundary in sorted(GRADE_BOUNDARIES.items(), key=lambda x: -x[1]):
        if marks >= boundary:
            return grade
    return 'E'  # Default fallback


def calculate_positions(exam: Exam):
    """
    Assign position per subject for all students in the exam.
    """
    subject_results = defaultdict(list)
    results = ExamResult.objects.filter(exam=exam).select_related('student', 'subject')

    for result in results:
        subject_results[result.subject_id].append(result)

    for subject_id, result_list in subject_results.items():
        result_list.sort(key=lambda r: r.marks if r.marks is not None else -1, reverse=True)

        position = 1
        last_marks = None
        same_rank_count = 0

        for idx, result in enumerate(result_list):
            if result.marks == last_marks:
                result.position = position
                same_rank_count += 1
            else:
                position = idx + 1
                result.position = position
                last_marks = result.marks
                same_rank_count = 1
            result.save(update_fields=["position"])


def calculate_total_and_average(exam: Exam):
    """
    Calculate total score and average marks for each student in the exam.
    """
    student_scores = ExamResult.objects.filter(exam=exam).values('student').annotate(
        total_marks=Sum('marks'),
        avg_marks=Avg('marks')
    )

    for entry in student_scores:
        student = Student.objects.get(id=entry['student'])
        student.total_marks = entry['total_marks'] or 0
        student.average_marks = round(entry['avg_marks'] or 0, 2)
        student.save(update_fields=["total_marks", "average_marks"])


def auto_post_marks(exam: Exam):
    """
    Auto-grades each mark, calculates position, total and average marks.
    Should be run after teachers finish entering marks.
    """
    results = ExamResult.objects.filter(exam=exam)

    for result in results:
        if result.marks is not None:
            result.grade = calculate_grade(result.marks)
            result.save(update_fields=["grade"])

    calculate_positions(exam)
    calculate_total_and_average(exam)


def generate_exam_predictions(student, subject=None):
    """
    AI-powered exam performance prediction stub.

    """
    base_score = getattr(student, 'average_marks', None)
    if base_score is None:
        # Default baseline prediction if no average_marks available
        base_score = 50

    # Add small random noise +/- 5 marks
    predicted_score = base_score + random.uniform(-5, 5)
    # Clamp between 0 and 100
    predicted_score = max(0, min(100, predicted_score))

    return round(predicted_score, 2)

def generate_ai_exam(*args, **kwargs):
    # TODO: implement this function later
    pass
