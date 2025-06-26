# assessments/tasks.py

from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

from assessments.models import (
    Assessment, AssessmentSession, StudentAnswer,
    AssessmentResult, RetakePolicy
)
from django.contrib.auth import get_user_model

from syllabus.models import SyllabusTopic
from notifications.utils import send_notification_to_user
from myproject.celery import app

User = get_user_model()


@app.task
def auto_grade_objective_assessments():
    """
    Automatically grades multiple choice and objective assessments
    that are pending grading and have an answer key.
    """
    pending_sessions = AssessmentSession.objects.filter(
        status='submitted',
        assessment__grading_mode='auto'
    )

    for session in pending_sessions:
        correct = 0
        total = 0

        for answer in session.answers.all():
            if answer.question.correct_choice and answer.selected_choice:
                total += 1
                if answer.selected_choice == answer.question.correct_choice:
                    correct += 1

        percentage = (correct / total) * 100 if total else 0
        AssessmentResult.objects.update_or_create(
            session=session,
            defaults={
                'score': percentage,
                'graded_on': timezone.now(),
                'graded_by': None,
                'status': 'graded'
            }
        )

        session.status = 'graded'
        session.save()

        send_notification_to_user(
            session.student.user,
            title="Assessment Graded",
            message=f"Your assessment for {session.assessment.title} has been auto-graded. Score: {percentage:.2f}%"
        )


@app.task
def remind_upcoming_assessments():
    """
    Sends reminders to students about upcoming assessments within the next 24 hours.
    """
    upcoming_assessments = Assessment.objects.filter(
        scheduled_date__range=[timezone.now(), timezone.now() + timedelta(hours=24)]
    )

    for assessment in upcoming_assessments:
        students = assessment.target_students.all()
        for student in students:
            send_notification_to_user(
                student.user,
                title="Upcoming Assessment Reminder",
                message=f"You have {assessment.title} scheduled for {assessment.scheduled_date.strftime('%Y-%m-%d %H:%M')}."
            )


@app.task
def generate_adaptive_followups():
    """
    For students with low performance, generate a suggested follow-up assessment (adaptive).
    """
    low_scores = AssessmentResult.objects.filter(score__lt=40)

    for result in low_scores:
        original = result.session.assessment
        topic = original.topic

        if not topic:
            continue

        # Optional: AI trigger to generate custom adaptive quiz (stubbed)
        # from .ai import generate_adaptive_quiz
        # generate_adaptive_quiz(student=result.session.student, topic=topic)

        send_notification_to_user(
            result.session.student.user,
            title="Adaptive Practice Suggested",
            message=f"We noticed you struggled with {topic.title}. A new practice quiz is available to help you improve!"
        )


@app.task
def archive_old_assessments():
    """
    Archives assessments older than X months.
    """
    threshold_date = timezone.now() - timedelta(days=180)
    outdated = Assessment.objects.filter(
        scheduled_date__lt=threshold_date,
        status__in=['completed', 'graded']
    )
    outdated.update(is_archived=True)


@app.task
def enforce_retake_policy():
    """
    Enforces retake policies on failed assessments.
    """
    failed_results = AssessmentResult.objects.filter(score__lt=50, retake_eligible=False)

    for result in failed_results:
        policy = RetakePolicy.objects.filter(assessment=result.session.assessment).first()
        if not policy:
            continue

        result.retake_eligible = True
        result.save()

        send_notification_to_user(
            result.session.student.user,
            title="Retake Available",
            message=f"A retake for {result.session.assessment.title} is now available based on your performance and policy."
        )
