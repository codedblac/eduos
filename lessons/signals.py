from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import LessonPlan, LessonSession
from notifications.utils import notify_user
from .ai import LessonAI  # Updated import


@receiver(post_save, sender=LessonPlan)
def notify_on_lesson_plan_creation(sender, instance, created, **kwargs):
    """
    Notify when a new lesson plan is created.
    Suggest scaffolding if missing fields like objectives/resources.
    """
    if created:
        message = (
            f"A new lesson plan has been created for {instance.subject.name} - "
            f"{instance.class_level.name}, Week {instance.week_number}."
        )

        if instance.teacher:
            notify_user(
                user=instance.teacher,
                title="New Lesson Plan Created",
                message=message,
                source_app='lessons'
            )

            # If objectives are missing, use LessonAI to suggest a template
            if not instance.objectives.strip():
                suggestion = LessonAI.suggest_lesson_template(
                    subject_id=instance.subject_id,
                    topic_id=instance.topic_id
                )
                if suggestion:
                    notify_user(
                        user=instance.teacher,
                        title="AI Lesson Plan Suggestions Available",
                        message="We noticed this plan has missing fields. AI suggestions are ready for review.",
                        source_app='lessons'
                    )


@receiver(post_save, sender=LessonSession)
def log_lesson_session_activity(sender, instance, created, **kwargs):
    """
    Log when a lesson session is created and notify the teacher.
    """
    if created and instance.lesson_schedule.lesson_plan.teacher:
        teacher = instance.lesson_schedule.lesson_plan.teacher
        subject = instance.lesson_schedule.lesson_plan.subject
        notify_user(
            user=teacher,
            title="Lesson Session Recorded",
            message=f"You have recorded a session for {subject.name} on {instance.delivered_on}.",
            source_app='lessons'
        )


@receiver(pre_delete, sender=LessonPlan)
def prevent_or_log_deletion(sender, instance, **kwargs):
    """
    Log or prevent deletion of a lesson plan with delivered sessions.
    """
    for schedule in instance.schedules.all():
        if hasattr(schedule, 'session'):
            raise Exception("Cannot delete a lesson plan with completed sessions.")
