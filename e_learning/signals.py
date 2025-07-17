from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    Assignment, AssignmentSubmission,
    QuizSubmission, LiveClassSession,
    CourseAnnouncement, Message,
    StudentLessonProgress, AIPredictedScore,
    CourseEnrollment, MessageThread
)
from notifications.utils import notify_user
from accounts.models import CustomUser


# -----------------------------
# ASSIGNMENTS
# -----------------------------

@receiver(post_save, sender=Assignment)
def notify_assignment_created(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for enrollment in course.enrollments.filter(is_active=True):
            notify_user(
                user=enrollment.student.user,
                title=f"New Assignment: {instance.title}",
                message=(
                    f"An assignment for '{course.title}' is due on "
                    f"{instance.due_date.strftime('%d %b %Y, %I:%M %p')}."
                ),
                notification_type="assignment"
            )


@receiver(post_save, sender=AssignmentSubmission)
def notify_assignment_submitted(sender, instance, created, **kwargs):
    if created:
        notify_user(
            user=instance.assignment.created_by,
            title="Assignment Submitted",
            message=f"{instance.student.full_name} submitted '{instance.assignment.title}'.",
            notification_type="assignment"
        )


# -----------------------------
# QUIZZES
# -----------------------------

@receiver(post_save, sender=QuizSubmission)
def notify_quiz_submitted(sender, instance, created, **kwargs):
    if created:
        notify_user(
            user=instance.quiz.created_by,
            title="Quiz Submitted",
            message=f"{instance.student.full_name} submitted quiz '{instance.quiz.title}'.",
            notification_type="quiz"
        )


# -----------------------------
# LIVE CLASSES
# -----------------------------

@receiver(post_save, sender=LiveClassSession)
def notify_live_class_created(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for enrollment in course.enrollments.filter(is_active=True):
            notify_user(
                user=enrollment.student.user,
                title=f"Live Class: {instance.title}",
                message=(
                    f"A live session has been scheduled for '{course.title}' "
                    f"on {instance.start_time.strftime('%d %b %Y, %I:%M %p')}."
                ),
                notification_type="live_class"
            )


# -----------------------------
# ANNOUNCEMENTS
# -----------------------------

@receiver(post_save, sender=CourseAnnouncement)
def notify_course_announcement(sender, instance, created, **kwargs):
    if created:
        course = instance.course
        for enrollment in course.enrollments.filter(is_active=True):
            notify_user(
                user=enrollment.student.user,
                title=f"Announcement: {instance.title}",
                message=instance.message,
                notification_type="announcement"
            )


# -----------------------------
# MESSAGE THREADS
# -----------------------------

@receiver(m2m_changed, sender=MessageThread.participants.through)
def notify_message_thread_join(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        new_users = CustomUser.objects.filter(pk__in=pk_set)
        for user in new_users:
            notify_user(
                user=user,
                title="Added to Conversation",
                message=f"You’ve been added to a course message thread for '{instance.course.title}'.",
                notification_type="message"
            )


@receiver(post_save, sender=Message)
def notify_message_sent(sender, instance, created, **kwargs):
    if created:
        participants = instance.thread.participants.exclude(id=instance.sender_id)
        for user in participants:
            notify_user(
                user=user,
                title="New Message",
                message=f"New message in thread for '{instance.thread.course.title}': {instance.content[:50]}...",
                notification_type="message"
            )


# -----------------------------
# PROGRESS TRACKING
# -----------------------------

@receiver(post_save, sender=StudentLessonProgress)
def notify_lesson_progress_updated(sender, instance, created, **kwargs):
    if instance.is_completed:
        notify_user(
            user=instance.student.user,
            title="Lesson Completed",
            message=f"You’ve completed the lesson: '{instance.lesson.title}'.",
            notification_type="progress"
        )


# -----------------------------
# AI SCORE ALERT
# -----------------------------

@receiver(post_save, sender=AIPredictedScore)
def notify_ai_prediction(sender, instance, created, **kwargs):
    notify_user(
        user=instance.student.user,
        title="Performance Prediction Updated",
        message=f"Your predicted score for '{instance.course.title}' is now {instance.predicted_score}%",
        notification_type="ai_score"
    )


# -----------------------------
# ENROLLMENT
# -----------------------------

@receiver(post_save, sender=CourseEnrollment)
def notify_course_enrollment(sender, instance, created, **kwargs):
    if created:
        notify_user(
            user=instance.student.user,
            title="Course Enrollment",
            message=f"You’ve been enrolled in the course '{instance.course.title}'.",
            notification_type="enrollment"
        )
