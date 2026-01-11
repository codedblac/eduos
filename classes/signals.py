# classes/signals.py

import uuid
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import ClassLevel, Stream, StudentStreamEnrollment
from .tasks import recompute_stream_analytics, recompute_class_level_analytics
from notifications.models import Notification


# ======================================================
# 🔹 Auto-generate Stream Code
# ======================================================
@receiver(pre_save, sender=Stream)
def auto_generate_stream_code(sender, instance, **kwargs):
    """
    Auto-generate a stream code if not provided.
    Scoped uniqueness is handled at DB level.
    """
    if not instance.code:
        base = instance.name.replace(" ", "").upper()
        suffix = uuid.uuid4().hex[:4].upper()
        instance.code = f"{base}-{suffix}"


# ======================================================
# 🔹 Notify Admins on ClassLevel Creation
# ======================================================
@receiver(post_save, sender=ClassLevel)
def notify_class_level_created(sender, instance, created, **kwargs):
    """
    Notify institution admins when a new class level is created.
    """
    if not created:
        return

    institution = instance.institution
    admins = institution.customuser_set.filter(is_staff=True)

    if admins.exists():
        notification = Notification.objects.create(
            institution=institution,
            title="New Class Level Created",
            message=f"A new class level '{instance.name}' has been created for {institution.name}.",
        )
        notification.target_users.set(admins)


# ======================================================
# 🔹 Notify Admins on Stream Creation
# ======================================================
@receiver(post_save, sender=Stream)
def notify_stream_created(sender, instance, created, **kwargs):
    """
    Notify admins when a new stream is created.
    """
    if not created:
        return

    class_level = instance.class_level
    institution = class_level.institution
    admins = institution.customuser_set.filter(is_staff=True)

    if admins.exists():
        notification = Notification.objects.create(
            institution=institution,
            title="New Stream Created",
            message=f"A new stream '{instance.name}' has been added to class level '{class_level.name}' ({instance.academic_year.name}).",
        )
        notification.target_users.set(admins)


# ======================================================
# 🔹 Enrollment Changes → Trigger Analytics
# ======================================================
@receiver(post_save, sender=StudentStreamEnrollment)
def handle_enrollment_change(sender, instance, created, **kwargs):
    """
    When enrollment changes, queue analytics recomputation.
    """
    stream = instance.stream
    class_level = stream.class_level
    academic_year = instance.academic_year

    # Recompute stream analytics
    recompute_stream_analytics.delay(
        stream_id=stream.id,
        academic_year_id=academic_year.id,
    )

    # Recompute class level analytics
    recompute_class_level_analytics.delay(
        class_level_id=class_level.id,
        academic_year_id=academic_year.id,
    )


# ======================================================
# 🔹 Handle Stream Deactivation
# ======================================================
@receiver(post_save, sender=Stream)
def handle_stream_deactivation(sender, instance, **kwargs):
    """
    If a stream is deactivated, recompute class level analytics.
    """
    if not instance.is_active:
        recompute_class_level_analytics.delay(
            class_level_id=instance.class_level.id,
            academic_year_id=instance.academic_year.id,
        )
