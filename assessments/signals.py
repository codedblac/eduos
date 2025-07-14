from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import (
    AssessmentSession,
    AssessmentVisibility,
    AssessmentLock,
    StudentAnswer,
    PerformanceTrend,
)
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP


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
    lock = getattr(instance.question.assessment, 'assessmentlock', None)
    if lock and lock.locked:
        raise ValueError("This assessment is locked and cannot be edited.")


@receiver(post_save, sender=AssessmentSession)
def update_performance_trend(sender, instance, created, **kwargs):
    """
    Update or create PerformanceTrend after a session is graded.
    """
    if not created and instance.is_graded and instance.score is not None:
        from .models import Term  # Avoid circular import

        trend, _ = PerformanceTrend.objects.get_or_create(
            student=instance.student,
            subject=instance.assessment.subject,
            term=instance.assessment.term,
            defaults={
                "average_score": Decimal(instance.score).quantize(Decimal('.01'), rounding=ROUND_HALF_UP),
                "assessment_count": 1,
            }
        )
        if not _:
            # Update existing
            total_score = (trend.average_score * trend.assessment_count) + instance.score
            trend.assessment_count += 1
            trend.average_score = Decimal(total_score / trend.assessment_count).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            trend.save()


@receiver(post_save, sender=StudentAnswer)
def auto_grade_mcq(sender, instance, created, **kwargs):
    """
    Automatically grade MCQs when saved.
    """
    if created and instance.question.type == 'mcq' and instance.selected_choice:
        if instance.selected_choice.is_correct:
            instance.marks_awarded = instance.question.marks
        else:
            instance.marks_awarded = 0
        instance.auto_graded = True
        instance.save(update_fields=['marks_awarded', 'auto_graded'])


# Optional: Notify teacher or student via Celery or signal hooks
# Example placeholder (extendable later)
def notify_user(user, message):
    print(f"[Notify] {user}: {message}")
