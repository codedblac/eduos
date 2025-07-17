from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models import Q, Avg
from .models import (
    Assignment, AssignmentSubmission, Quiz, QuizSubmission,
    LiveClassSession, CourseEnrollment, StudentLessonProgress,
    AIPredictedScore
)
from notifications.utils import notify_user, notify_group
from datetime import timedelta


@shared_task
def send_assignment_reminders():
    """
    Notify students of upcoming assignment deadlines within 48 hours.
    """
    now = timezone.now()
    upcoming = Assignment.objects.filter(due_date__range=(now, now + timedelta(hours=48)))

    for assignment in upcoming:
        enrolled_students = assignment.course.enrollments.filter(is_active=True)
        for enrollment in enrolled_students:
            notify_user(
                user=enrollment.student.user,
                title=f"Upcoming Assignment: {assignment.title}",
                message=f"The assignment is due on {assignment.due_date.strftime('%d %b %Y, %I:%M %p')}."
            )


@shared_task
def auto_grade_quizzes():
    """
    Grade submitted quizzes that haven’t been graded yet.
    """
    ungraded = QuizSubmission.objects.filter(score__isnull=True)

    for submission in ungraded:
        correct = 0
        total = submission.quiz.questions.count()

        for question in submission.quiz.questions.all():
            student_answer = submission.answers.get(str(question.id), "").strip().lower()
            correct_answer = question.correct_answer.strip().lower()
            if student_answer == correct_answer:
                correct += 1

        score = round((correct / total) * 100, 2) if total > 0 else 0.0
        submission.score = score
        submission.save()

        notify_user(
            user=submission.student.user,
            title="Quiz Graded",
            message=f"Your quiz '{submission.quiz.title}' has been graded. You scored {score}%."
        )


@shared_task
def log_missed_live_sessions():
    """
    Log missed attendance for past live sessions with attendance_required=True.
    """
    now = timezone.now()
    past_sessions = LiveClassSession.objects.filter(
        end_time__lt=now,
        attendance_required=True
    )

    for session in past_sessions:
        enrolled_students = session.course.enrollments.filter(is_active=True)
        for enrollment in enrolled_students:
            if not session.liveattendance_set.filter(student=enrollment.student).exists():
                session.liveattendance_set.create(
                    student=enrollment.student,
                    is_present=False,
                    timestamp=now
                )


@shared_task
def generate_predicted_scores():
    """
    AI model placeholder to calculate predicted scores based on engagement.
    """
    for enrollment in CourseEnrollment.objects.filter(is_active=True):
        student = enrollment.student
        course = enrollment.course

        progress = StudentLessonProgress.objects.filter(
            student=student, lesson__chapter__course=course
        )

        if not progress.exists():
            continue

        completed_ratio = progress.filter(is_completed=True).count() / progress.count()
        watched_time = progress.aggregate(total=Avg('watched_duration'))['total'] or 0
        score = round((completed_ratio * 70) + min(watched_time, 60) * 0.5, 2)

        AIPredictedScore.objects.update_or_create(
            student=student,
            course=course,
            defaults={"predicted_score": score}
        )


@shared_task
def clean_old_submissions(days=90):
    """
    Deletes submissions older than specified days to free up storage.
    """
    threshold = timezone.now() - timedelta(days=days)
    AssignmentSubmission.objects.filter(submitted_at__lt=threshold).delete()
    QuizSubmission.objects.filter(submitted_at__lt=threshold).delete()
