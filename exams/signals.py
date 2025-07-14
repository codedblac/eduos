# exams/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Max, Min, Count
from django.utils.timezone import now

from .models import ExamResult, StudentScore, ExamInsight, Exam, ExamSubject
from .tasks import generate_exam_insights, archive_old_exams

from celery import shared_task


@receiver(post_save, sender=ExamResult)
def trigger_exam_insight_on_result_save(sender, instance, created, **kwargs):
    """
    Generate insights for the exam when a new result is saved.
    """
    try:
        generate_exam_insights.delay(instance.exam.id)
    except Exception as e:
        print(f"[Signal Error] Failed to trigger insight generation: {str(e)}")


@receiver(post_save, sender=StudentScore)
def update_subject_positions(sender, instance, **kwargs):
    """
    Update student rankings per subject after score is saved.
    """
    try:
        scores = StudentScore.objects.filter(
            exam_subject=instance.exam_subject
        ).order_by('-score')

        for idx, score in enumerate(scores, start=1):
            if score.position != idx:
                score.position = idx
                score.save(update_fields=['position'])

    except Exception as e:
        print(f"[Signal Error] Failed to update positions: {str(e)}")


@receiver(post_save, sender=ExamResult)
def update_overall_exam_ranks(sender, instance, **kwargs):
    """
    Re-rank all students in the exam by average score.
    """
    try:
        results = ExamResult.objects.filter(
            exam=instance.exam
        ).order_by('-average_score')

        for idx, result in enumerate(results, start=1):
            if result.overall_position != idx:
                result.overall_position = idx
                result.save(update_fields=['overall_position'])

    except Exception as e:
        print(f"[Signal Error] Failed to re-rank students: {str(e)}")


@receiver(post_save, sender=Exam)
def auto_trigger_archival(sender, instance, **kwargs):
    """
    Archive old exams (3+ years ago) automatically.
    """
    try:
        if instance.year <= (now().year - 3):
            archive_old_exams.delay()
    except Exception as e:
        print(f"[Signal Error] Archival task failed: {str(e)}")


@receiver(post_delete, sender=Exam)
def cleanup_exam_insights_on_delete(sender, instance, **kwargs):
    """
    Delete all related insights when an exam is deleted.
    """
    try:
        ExamInsight.objects.filter(exam=instance).delete()
    except Exception as e:
        print(f"[Signal Error] Failed to clean up exam insights: {str(e)}")


@receiver(post_delete, sender=StudentScore)
def rerank_subject_after_score_delete(sender, instance, **kwargs):
    """
    Recalculate subject-level positions if a score is deleted.
    """
    try:
        scores = StudentScore.objects.filter(
            exam_subject=instance.exam_subject
        ).order_by('-score')

        for idx, score in enumerate(scores, start=1):
            if score.position != idx:
                score.position = idx
                score.save(update_fields=['position'])
    except Exception as e:
        print(f"[Signal Error] Failed to rerank subject scores after delete: {str(e)}")


@receiver(post_delete, sender=ExamResult)
def rerank_exam_after_result_delete(sender, instance, **kwargs):
    """
    Recalculate overall exam rankings if a result is deleted.
    """
    try:
        results = ExamResult.objects.filter(
            exam=instance.exam
        ).order_by('-average_score')

        for idx, result in enumerate(results, start=1):
            if result.overall_position != idx:
                result.overall_position = idx
                result.save(update_fields=['overall_position'])
    except Exception as e:
        print(f"[Signal Error] Failed to rerank exam results after delete: {str(e)}")
