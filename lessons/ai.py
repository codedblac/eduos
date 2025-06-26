from syllabus.models import SyllabusTopic, SyllabusSubtopic
from lessons.models import LessonPlan
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count


def generate_lesson_plan_suggestions():
    """
    Suggest upcoming lessons based on topics not yet covered.
    Could be triggered weekly.
    """
    suggestions = []
    now = timezone.now()

    topics = SyllabusTopic.objects.annotate(
        plans=Count('lessonplan')
    ).filter(plans=0)

    for topic in topics:
        subtopics = SyllabusSubtopic.objects.filter(topic=topic)
        for sub in subtopics:
            suggestion = {
                "topic": topic.title,
                "subtopic": sub.title,
                "suggested_week": now.isocalendar().week + 1,
                "objectives": getattr(sub, 'objectives', "TBD"),
            }
            suggestions.append(suggestion)
    return suggestions


def predict_uncovered_topics():
    """
    Identify topics likely to remain uncovered by term end based on past pace.
    """
    warnings = []
    term_end = timezone.now() + timedelta(weeks=5)  # Placeholder
    for plan in LessonPlan.objects.all():
        total = plan.schedules.count()
        delivered = plan.schedules.filter(session__isnull=False).count()
        if total == 0:
            continue
        pace = delivered / total
        weeks_remaining = (term_end - timezone.now()).days / 7
        projected = delivered + (pace * weeks_remaining)
        if projected < total:
            warnings.append({
                'teacher': plan.teacher.username,
                'subject': plan.subject.name,
                'class': plan.class_level.name,
                'message': 'You may not complete the syllabus at current pace.'
            })
    return warnings
