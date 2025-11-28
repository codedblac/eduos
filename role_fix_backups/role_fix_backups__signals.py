# id_cards/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUser
from students.models import Student
from teachers.models import Teacher
from .tasks import generate_id_card, regenerate_id_cards_on_profile_update


# --- STUDENT ID CARD SIGNALS ---

@receiver(post_save, sender=Student)
def student_id_card_handler(sender, instance, created, **kwargs):
    """
    Handle ID card generation and regeneration for students.
    """
    if created:
        generate_id_card.delay(user_id=instance.id, role='student')
    elif instance.user:
        regenerate_id_cards_on_profile_update.delay(user_id=instance.user.id)


# --- TEACHER ID CARD SIGNALS ---

@receiver(post_save, sender=Teacher)
def teacher_id_card_handler(sender, instance, created, **kwargs):
    """
    Handle ID card generation and regeneration for teachers.
    """
    if created:
        generate_id_card.delay(user_id=instance.id, role='teacher')
    elif instance.user:
        regenerate_id_cards_on_profile_update.delay(user_id=instance.user.id)


# --- STAFF / ADMIN ID CARD SIGNALS ---

@receiver(post_save, sender=CustomUser)
def staff_admin_id_card_handler(sender, instance, created, **kwargs):
    """
    Handle ID card generation and regeneration for non-teaching staff or admins.
    """
    if instance.role in ['admin', 'staff']:
        if created:
            generate_id_card.delay(user_id=instance.id, role=instance.role)
        else:
            regenerate_id_cards_on_profile_update.delay(user_id=instance.id)
