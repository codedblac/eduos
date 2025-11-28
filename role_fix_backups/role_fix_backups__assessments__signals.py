from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

from .models import (
    AssessmentSession,
    AssessmentVisibility,
    AssessmentLock,
    StudentAnswer,
    PerformanceTrend,
)

@receiver(post_save, sender=AssessmentSession)
def create_visibility_for_session(sender, instance, created, **kwargs):
    """
    Automatically create an AssessmentVisibility record when a new session starts.
    """
    if created:
        AssessmentVisibility.objects.get_or_create(session=instance)


@receiver(pre_save, sender=StudentAnswer)
def prevent_edits_to_locked_assessments(sender, instance, **kwargs):
    """
    Prevent saving answers to locked assessments.
    """
    try:
        lock = instance.question.assessment.assessmentlock
        if lock.locked:
            raise ValueError("This assessment is locked and cannot be edited.")
    except AssessmentLock.DoesNotExist:
        pass


@receiver(post_save, sender=AssessmentSession)
def update_performance_trend(sender, instance, created, **kwargs):
    """
    Update or create PerformanceTrend after a session is graded.
    """
    if not created and instance.is_graded and instance.score is not None:
        from .models import Term  # Avoid circular import

        score = Decimal(instance.score).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        trend, created_trend = PerformanceTrend.objects.get_or_create(
            student=instance.student,
            subject=instance.assessment.subject,
            term=instance.assessment.term,
            defaults={
                "average_score": score,
                "assessment_count": 1,
            }
        )
        if not created_trend:
            total_score = (trend.average_score * trend.assessment_count) + score
            trend.assessment_count += 1
            trend.average_score = Decimal(total_score / trend.assessment_count).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            trend.save()


@receiver(post_save, sender=StudentAnswer)
def auto_grade_mcq(sender, instance, created, **kwargs):
    """
    Automatically grade MCQs when saved.
    """
    if created and instance.question.type == 'mcq' and instance.selected_choice:
        instance.marks_awarded = instance.question.marks if instance.selected_choice.is_correct else 0
        instance.auto_graded = True
        instance.save(update_fields=['marks_awarded', 'auto_graded'])


# Optional: Example notification function to be extended via Celery
def notify_user(user, message):
    # Extend this with Celery or WebSocket/Redis-based real-time notification
    print(f"[Notify] {user.username}: {message}")
