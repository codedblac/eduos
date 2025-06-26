from collections import defaultdict
from django.db.models import Avg, Count, Q
from assessments.models import (
    Assessment, AssessmentSession, StudentAnswer,
    AssessmentResult, Question, AssessmentType
)
from students.models import Student
from subjects.models import Subject
from django.utils import timezone


def overall_performance_summary(institution):
    """
    Generate overall assessment performance analytics for the institution.
    """
    data = AssessmentResult.objects.filter(
        assessment__institution=institution
    ).values('assessment__subject__name').annotate(
        avg_score=Avg('score'),
        total=Count('id')
    )
    return list(data)


def student_performance_trend(student):
    """
    Return chronological trend of student's performance.
    """
    results = AssessmentResult.objects.filter(
        student=student
    ).order_by('assessment__date')

    return [
        {
            'assessment': result.assessment.title,
            'score': result.score,
            'date': result.assessment.date
        }
        for result in results
    ]


def subject_coverage_analysis(subject):
    """
    Calculate topic coverage based on assessments administered for a subject.
    """
    questions = Question.objects.filter(subject=subject)
    topic_distribution = defaultdict(int)

    for q in questions:
        if q.topic:
            topic_distribution[q.topic.title] += 1

    return dict(topic_distribution)


def flagged_students_for_inconsistency(institution):
    """
    Detect students with abnormal score patterns for possible cheating or issues.
    """
    flagged = []
    students = Student.objects.filter(institution=institution)

    for student in students:
        scores = list(AssessmentResult.objects.filter(student=student).values_list('score', flat=True))
        if len(scores) >= 3:
            std_dev = (max(scores) - min(scores)) / 2
            if std_dev > 25:
                flagged.append({
                    'student_id': student.id,
                    'name': student.full_name,
                    'note': 'Inconsistent performance patterns across assessments.'
                })
    return flagged


def topic_mastery_heatmap(student):
    """
    Generate a heatmap data structure showing topic-wise mastery by student.
    """
    answers = StudentAnswer.objects.filter(session__student=student)
    heatmap = defaultdict(lambda: {'correct': 0, 'total': 0})

    for answer in answers:
        if answer.question and answer.question.topic:
            key = answer.question.topic.title
            heatmap[key]['total'] += 1
            if answer.is_correct:
                heatmap[key]['correct'] += 1

    for topic in heatmap:
        correct = heatmap[topic]['correct']
        total = heatmap[topic]['total']
        heatmap[topic]['mastery_percent'] = round((correct / total) * 100, 2) if total > 0 else 0

    return heatmap


def assessment_participation_rate(assessment):
    """
    Check how many students attempted an assessment vs expected.
    """
    total_students = assessment.assigned_to.count()
    sessions = AssessmentSession.objects.filter(assessment=assessment).count()

    return {
        "total_assigned": total_students,
        "attempted": sessions,
        "completion_rate": round((sessions / total_students) * 100, 2) if total_students > 0 else 0
    }
