from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Assessment, AssessmentSession,  StudentAnswer
from notifications.utils import send_notification_to_user
from accounts.models import CustomUser


@receiver(post_save, sender=Assessment)
def notify_teachers_on_assessment_creation(sender, instance, created, **kwargs):
    if created:
        teachers = CustomUser.objects.filter(assigned_subjects=instance.subject)
        for teacher in teachers:
            send_notification_to_user(
                user=teacher,
                title="New Assessment Created",
                message=f"A new assessment for {instance.subject.name} has been created."
            )


@receiver(post_save, sender=AssessmentSession)
def notify_student_on_assessment_assigned(sender, instance, created, **kwargs):
    if created:
        send_notification_to_user(
            user=instance.student,
            title="New Assessment Assigned",
            message=f"You have a new assessment: {instance.assessment.title}. Please complete it before {instance.assessment.due_date}."
        )


@receiver(post_save, sender=StudentAnswer)
def auto_mark_mcq_answer(sender, instance, created, **kwargs):
    if created and instance.question.type == 'mcq':
        correct_answer = instance.question.answer_choices.filter(is_correct=True).first()
        if correct_answer and instance.selected_choice == correct_answer:
            instance.is_correct = True
            instance.score = instance.question.max_score
        else:
            instance.is_correct = False
            instance.score = 0
        instance.save(update_fields=["is_correct", "score"])


# @receiver(post_save, sender=AssessmentResult)
# def notify_student_on_result_posted(sender, instance, created, **kwargs):
#     if created:
#         send_notification_to_user(
#             user=instance.student,
#             title="Assessment Results Available",
#             message=f"Your results for {instance.assessment.title} are now available. Grade: {instance.grade}."
#         )
