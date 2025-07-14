# exams/grading_engine.py

from typing import Optional, Dict
from django.db.models import F
from .models import Exam, ExamResult, StudentScore, GradeBoundary, ExamSubject
from students.models import Student
from subjects.models import Subject

# Default grade thresholds (used if no custom ones exist)
DEFAULT_GRADE_BOUNDARIES: Dict[str, int] = {
    'A': 80, 'A-': 75, 'B+': 70, 'B': 65, 'B-': 60,
    'C+': 55, 'C': 50, 'C-': 45, 'D+': 40, 'D': 35, 'E': 0
}

# Human-readable remarks per grade
GRADE_REMARKS: Dict[str, str] = {
    'A': 'Excellent', 'A-': 'Very Good', 'B+': 'Good', 'B': 'Above Average',
    'B-': 'Satisfactory', 'C+': 'Fair', 'C': 'Pass', 'C-': 'Bare Pass',
    'D+': 'Weak', 'D': 'Poor', 'E': 'Fail', 'N/A': 'Incomplete'
}


def get_grade_boundaries(institution, subject) -> Dict[str, int]:
    """
    Fetch institution-specific grade boundaries for a subject.
    Falls back to default if none are found.
    """
    boundaries = GradeBoundary.objects.filter(
        institution=institution,
        subject=subject
    ).order_by('-min_score')

    if not boundaries.exists():
        return DEFAULT_GRADE_BOUNDARIES

    return {b.grade: b.min_score for b in boundaries}


def get_grade(score: Optional[float], boundaries: Dict[str, int]) -> str:
    """
    Determine grade based on score and grading boundaries.
    """
    if score is None:
        return "N/A"

    for grade, cutoff in sorted(boundaries.items(), key=lambda x: -x[1]):
        if score >= cutoff:
            return grade
    return "E"  # Fallback (should not reach if boundaries are correct)


def get_remark(grade: str) -> str:
    """
    Map grade to human-readable remark.
    """
    return GRADE_REMARKS.get(grade, "Unknown")


def grade_student_score(score: StudentScore) -> None:
    """
    Grade an individual student's subject score.
    """
    exam_subject = score.exam_subject
    boundaries = get_grade_boundaries(exam_subject.exam.institution, exam_subject.subject)

    score.grade = get_grade(score.score, boundaries)
    score.remarks = get_remark(score.grade)
    score.save(update_fields=["grade", "remarks"])


def grade_all_subject_scores(exam: Exam) -> None:
    """
    Grade all StudentScores in an exam.
    """
    scores = StudentScore.objects.filter(exam_subject__exam=exam).select_related('exam_subject__subject', 'exam_subject__exam')
    for score in scores:
        grade_student_score(score)


def grade_exam_result(result: ExamResult) -> None:
    """
    Assign final grade to an ExamResult based on total score.
    """
    exam = result.exam
    subject = Subject.objects.filter(examsubject__exam=exam).first()
    boundaries = get_grade_boundaries(exam.institution, subject or Subject.objects.first())

    result.grade = get_grade(result.total_score, boundaries)
    result.save(update_fields=["grade"])


def rank_students_by_exam(exam: Exam) -> None:
    """
    Rank students in an exam by their average score.
    """
    results = ExamResult.objects.filter(exam=exam).order_by('-average_score')

    rank = 1
    previous_score = None
    tied_count = 0

    for result in results:
        if result.average_score != previous_score:
            rank += tied_count
            tied_count = 1
        else:
            tied_count += 1

        previous_score = result.average_score
        result.overall_position = rank
        result.save(update_fields=["overall_position"])


def rank_scores_by_subject(exam: Exam) -> None:
    """
    Rank students per subject based on score.
    """
    subjects = ExamSubject.objects.filter(exam=exam)

    for exam_subject in subjects:
        scores = StudentScore.objects.filter(exam_subject=exam_subject).order_by('-score')

        rank = 1
        previous_score = None
        tied_count = 0

        for score in scores:
            if score.score != previous_score:
                rank += tied_count
                tied_count = 1
            else:
                tied_count += 1

            previous_score = score.score
            score.position = rank
            score.save(update_fields=["position"])


def grade_full_exam_pipeline(exam: Exam) -> None:
    """
    Run grading, ranking, and remarks for a full exam session.
    """
    grade_all_subject_scores(exam)

    for result in ExamResult.objects.filter(exam=exam):
        grade_exam_result(result)

    rank_students_by_exam(exam)
    rank_scores_by_subject(exam)
