# id_cards/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from accounts.models import CustomUser
from students.models import Student
from teachers.models import Teacher
from .tasks import generate_id_card, regenerate_id_cards_on_profile_update
from .models import IDCard

# Auto-generate ID card on student creation
@receiver(post_save, sender=Student)
def create_student_id_card(sender, instance, created, **kwargs):
    if created:
        generate_id_card.delay(user_id=instance.id, role='student')

# Regenerate ID if student profile is updated
@receiver(post_save, sender=Student)
def update_student_id_card(sender, instance, created, **kwargs):
    if not created:
        regenerate_id_cards_on_profile_update.delay(user_id=instance.user.id)

# Auto-generate ID card on teacher creation
@receiver(post_save, sender=Teacher)
def create_teacher_id_card(sender, instance, created, **kwargs):
    if created:
        generate_id_card.delay(user_id=instance.id, role='teacher')

# Regenerate ID if teacher profile is updated
@receiver(post_save, sender=Teacher)
def update_teacher_id_card(sender, instance, created, **kwargs):
    if not created:
        regenerate_id_cards_on_profile_update.delay(user_id=instance.user.id)

# Auto-generate/re-generate ID card for non-teaching staff & admins
@receiver(post_save, sender=CustomUser)
def handle_staff_id_card(sender, instance, created, **kwargs):
    if instance.role in ['admin', 'staff']:
        if created:
            generate_id_card.delay(user_id=instance.id, role=instance.role)
        else:
            regenerate_id_cards_on_profile_update.delay(user_id=instance.id)
