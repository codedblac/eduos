from typing import Dict, List
from collections import defaultdict

from django.db.models import Avg, Count, Q, StdDev
from django.utils import timezone

from assessments.models import (
    Assessment, AssessmentSession, StudentAnswer,
    AssessmentResult, Question, AssessmentType
)
from students.models import Student
from subjects.models import Subject


def overall_performance_summary(institution) -> List[Dict]:
    """
    Average score per subject for a given institution.
    """
    return list(
        AssessmentResult.objects.filter(
            assessment__institution=institution
        ).values('assessment__subject__name').annotate(
            avg_score=Avg('score'),
            total=Count('id')
        ).order_by('assessment__subject__name')
    )


def student_performance_trend(student: Student) -> List[Dict]:
    """
    Return student's assessment performance trend chronologically.
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


def subject_coverage_analysis(subject: Subject) -> Dict[str, int]:
    """
    Count how many questions have been tagged per topic for a subject.
    """
    questions = Question.objects.filter(subject=subject).select_related('topic')
    topic_counts = defaultdict(int)

    for q in questions:
        if q.topic:
            topic_counts[q.topic.title] += 1

    return dict(topic_counts)


def flagged_students_for_inconsistency(institution) -> List[Dict]:
    """
    Flag students with inconsistent score patterns using score range.
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


def topic_mastery_heatmap(student: Student) -> Dict[str, Dict]:
    """
    Return topic-wise accuracy breakdown for a student.
    """
    answers = StudentAnswer.objects.filter(session__student=student).select_related('question__topic')
    heatmap = defaultdict(lambda: {'correct': 0, 'total': 0})

    for answer in answers:
        topic = answer.question.topic if answer.question else None
        if topic:
            key = topic.title
            heatmap[key]['total'] += 1
            if getattr(answer, 'is_correct', False):
                heatmap[key]['correct'] += 1

    for topic in heatmap:
        correct = heatmap[topic]['correct']
        total = heatmap[topic]['total']
        heatmap[topic]['mastery_percent'] = round((correct / total) * 100, 2) if total else 0

    return dict(heatmap)


def assessment_participation_rate(assessment: Assessment) -> Dict:
    """
    How many students attempted vs expected for an assessment.
    """
    total_assigned = assessment.assigned_to.count() if hasattr(assessment, 'assigned_to') else 0
    attempted = AssessmentSession.objects.filter(assessment=assessment).count()

    return {
        "total_assigned": total_assigned,
        "attempted": attempted,
        "completion_rate": round((attempted / total_assigned) * 100, 2) if total_assigned else 0
    }


def assessment_type_distribution(institution) -> Dict[str, int]:
    """
    Count how many assessments of each type exist within an institution.
    """
    distribution = Assessment.objects.filter(
        institution=institution
    ).values('type__name').annotate(total=Count('id'))

    return {entry['type__name']: entry['total'] for entry in distribution}


def top_performing_students(institution, limit=10) -> List[Dict]:
    """
    Top N students by average assessment score.
    """
    return list(
        AssessmentResult.objects.filter(
            assessment__institution=institution
        ).values('student__id', 'student__full_name')
        .annotate(avg_score=Avg('score'))
        .order_by('-avg_score')[:limit]
    )


def subject_difficulty_ranking(institution) -> List[Dict]:
    """
    Subjects ranked by average student performance — lower = harder.
    """
    return list(
        AssessmentResult.objects.filter(
            assessment__institution=institution
        ).values('assessment__subject__name')
        .annotate(avg_score=Avg('score'))
        .order_by('avg_score')
    )
