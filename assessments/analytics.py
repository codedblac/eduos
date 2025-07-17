from typing import Dict, List
from collections import defaultdict

from django.db.models import Avg, Count, Q
from django.utils import timezone

from assessments.models import (
    Assessment, AssessmentSession, StudentAnswer,
    AssessmentResult, Question, AssessmentType
)
from students.models import Student
from subjects.models import Subject


def get_overall_performance_summary(institution) -> List[Dict]:
    """
    Returns average score and total assessments per subject for the institution.
    """
    return list(
        AssessmentResult.objects.filter(
            assessment__institution=institution
        ).values('assessment__subject__name')
        .annotate(
            avg_score=Avg('score'),
            total=Count('id')
        ).order_by('assessment__subject__name')
    )


def get_student_performance_trend(student: Student) -> List[Dict]:
    """
    Returns chronological performance trend for a student across assessments.
    """
    results = AssessmentResult.objects.filter(
        student=student
    ).select_related('assessment').order_by('assessment__scheduled_date')

    return [
        {
            'assessment': r.assessment.title,
            'score': r.score,
            'date': r.assessment.scheduled_date,
        }
        for r in results
    ]


def get_subject_coverage_analysis(subject: Subject) -> Dict[str, int]:
    """
    Returns a topic-wise question distribution for a subject.
    """
    questions = Question.objects.filter(subject=subject).select_related('topic')
    topic_counts = defaultdict(int)

    for question in questions:
        if question.topic:
            topic_counts[question.topic.title] += 1

    return dict(topic_counts)


def get_flagged_students(institution) -> List[Dict]:
    """
    Flags students with inconsistent score patterns (e.g., deviation > 30).
    """
    flagged = []
    students = Student.objects.filter(institution=institution)

    for student in students:
        scores = list(
            AssessmentResult.objects.filter(student=student)
            .values_list('score', flat=True)
        )
        if len(scores) >= 3:
            deviation = max(scores) - min(scores)
            if deviation > 30:
                flagged.append({
                    'student_id': student.id,
                    'name': student.full_name,
                    'note': 'Significant inconsistency detected.',
                    'min_score': min(scores),
                    'max_score': max(scores),
                    'std_dev': round(deviation / 2, 2),
                })

    return flagged


def get_topic_mastery_heatmap(student: Student) -> Dict[str, Dict]:
    """
    Returns a heatmap showing topic-wise mastery (correct/total ratio).
    """
    answers = StudentAnswer.objects.filter(
        session__student=student
    ).select_related('question__topic')

    heatmap = defaultdict(lambda: {'correct': 0, 'total': 0})

    for answer in answers:
        topic = answer.question.topic if answer.question else None
        if topic:
            topic_title = topic.title
            heatmap[topic_title]['total'] += 1
            if getattr(answer, 'is_correct', False):
                heatmap[topic_title]['correct'] += 1

    for topic_title in heatmap:
        correct = heatmap[topic_title]['correct']
        total = heatmap[topic_title]['total']
        heatmap[topic_title]['mastery_percent'] = round((correct / total) * 100, 2) if total else 0

    return dict(heatmap)


def get_assessment_participation_rate(assessment: Assessment) -> Dict:
    """
    Returns participation data for a specific assessment.
    """
    total_assigned = assessment.assigned_to.count() if hasattr(assessment, 'assigned_to') else 0
    attempted = AssessmentSession.objects.filter(assessment=assessment).count()

    return {
        "total_assigned": total_assigned,
        "attempted": attempted,
        "completion_rate": round((attempted / total_assigned) * 100, 2) if total_assigned else 0
    }


def get_assessment_type_distribution(institution) -> Dict[str, int]:
    """
    Returns distribution of assessments by type within an institution.
    """
    distribution = Assessment.objects.filter(
        institution=institution
    ).values('type__name').annotate(total=Count('id'))

    return {entry['type__name']: entry['total'] for entry in distribution}


def get_top_performing_students(institution, limit=10) -> List[Dict]:
    """
    Returns top N students with the highest average assessment scores.
    """
    return list(
        AssessmentResult.objects.filter(
            assessment__institution=institution
        ).values('student__id', 'student__full_name')
        .annotate(avg_score=Avg('score'))
        .order_by('-avg_score')[:limit]
    )


def get_subject_difficulty_ranking(institution) -> List[Dict]:
    """
    Ranks subjects by average performance (lowest first = hardest).
    """
    return list(
        AssessmentResult.objects.filter(
            assessment__institution=institution
        ).values('assessment__subject__name')
        .annotate(avg_score=Avg('score'))
        .order_by('avg_score')
    )
