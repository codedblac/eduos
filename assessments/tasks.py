from django.utils import timezone
from datetime import timedelta
from celery import shared_task

from .models import (
    Assessment, AssessmentSession, AssessmentLock, RetakePolicy,
    PerformanceTrend, Student, Subject, Term, AssessmentType
)
from notifications.utils import send_notification  # Assuming reusable utility
from assessments.utils import generate_assessment_from_template  # Custom generator
from django.db.models import Avg, Count


@shared_task
def auto_generate_assessments():
    """
    Periodically generate AI/manual assessments from templates for remote students.
    Triggered via scheduler or admin.
    """
    from .models import AssessmentTemplate

    templates = AssessmentTemplate.objects.filter(is_active=True)
    now_time = timezone.now()

    for template in templates:
        subject = template.type.subject_set.first()  # You may need to refine this
        if not subject:
            continue

        for class_level in subject.class_levels.all():
            assessment = generate_assessment_from_template(
                template=template,
                subject=subject,
                class_level=class_level,
                scheduled_date=now_time + timedelta(days=2)
            )
            print(f"Generated: {assessment}")


@shared_task
def disburse_assessments():
    """
    Sends notifications or schedules printable assessments to students.
    """
    now_time = timezone.now()
    assessments = Assessment.objects.filter(
        is_published=True,
        scheduled_date__lte=now_time + timedelta(hours=6),
        scheduled_date__gte=now_time
    )

    for assessment in assessments:
        sessions = AssessmentSession.objects.filter(assessment=assessment)
        for session in sessions:
            send_notification(
                user=session.student.user,
                title="Upcoming Assessment",
                message=f"You have '{assessment.title}' scheduled soon."
            )


@shared_task
def lock_past_due_assessments():
    """
    Locks assessments that have passed their submission window.
    """
    now_time = timezone.now()
    assessments = Assessment.objects.filter(scheduled_date__lt=now_time)

    for assessment in assessments:
        lock, created = AssessmentLock.objects.get_or_create(assessment=assessment)
        if not lock.locked:
            lock.locked = True
            lock.locked_at = now_time
            lock.reason = "Scheduled time elapsed"
            lock.save()


@shared_task
def enforce_retake_policies():
    """
    Prevents students from retaking assessments before cooldown or max attempts.
    """
    now_time = timezone.now()
    for policy in RetakePolicy.objects.all():
        attempts = AssessmentSession.objects.filter(
            assessment=policy.assessment,
            student__in=Student.objects.all()
        ).count()
        if attempts >= policy.max_attempts:
            AssessmentLock.objects.update_or_create(
                assessment=policy.assessment,
                defaults={"locked": True, "reason": "Retake limit reached"}
            )


@shared_task
def update_performance_trends():
    """
    Update each student's subject trend.
    """
    for student in Student.objects.all():
        for subject in Subject.objects.all():
            sessions = AssessmentSession.objects.filter(
                student=student, assessment__subject=subject, is_graded=True
            )
            if sessions.exists():
                avg_score = sessions.aggregate(avg=Avg('score'))['avg']
                count = sessions.count()
                term = sessions.order_by('-started_at').first().assessment.term

                PerformanceTrend.objects.update_or_create(
                    student=student,
                    subject=subject,
                    term=term,
                    defaults={
                        "average_score": avg_score,
                        "assessment_count": count,
                    }
                )
