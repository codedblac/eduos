from lessons.models import LessonPlan, LessonSession, LessonSchedule
from django.db.models import Count, Avg, Q
from datetime import timedelta
from django.utils import timezone


def get_teacher_workload(teacher):
    """
    Returns the total number of lesson plans and sessions for a given teacher.
    """
    return {
        "lesson_plans": LessonPlan.objects.filter(teacher=teacher).count(),
        "lesson_sessions": LessonSession.objects.filter(recorded_by=teacher).count(),
    }


def get_lesson_coverage_report(term):
    """
    Returns syllabus coverage percentage for all classes/subjects in a term.
    """
    report = []
    plans = LessonPlan.objects.filter(term=term)

    for plan in plans:
        total = plan.schedules.count()
        covered = plan.schedules.filter(session__coverage_status='covered').count()
        percent = (covered / total) * 100 if total else 0
        report.append({
            "subject": plan.subject.name,
            "class": plan.class_level.name,
            "teacher": plan.teacher.username,
            "coverage": round(percent, 1),
        })
    return report


def get_missed_lessons_stats():
    """
    Aggregate missed lessons per teacher and class.
    """
    missed = LessonSchedule.objects.filter(status='missed')
    return missed.values('lesson_plan__teacher__username', 'lesson_plan__class_level__name') \
        .annotate(total_missed=Count('id'))


def get_average_lesson_duration():
    """
    Computes average lesson duration by teacher or subject.
    """
    return LessonPlan.objects.values('teacher__username', 'subject__name') \
        .annotate(avg_duration=Avg('duration_minutes'))
