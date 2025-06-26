from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import AcademicYear, Term, AcademicEvent, HolidayBreak, AcademicAuditLog
from accounts.models import CustomUser
from django.utils.timezone import now


def get_actor():
    # In production, capture from request middleware or threading.local
    return None

@receiver(post_save, sender=AcademicYear)
def log_academic_year_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    AcademicAuditLog.objects.create(
        actor=get_actor(),
        action=action,
        model_name='AcademicYear',
        record_id=instance.id,
        timestamp=now(),
        notes=f"AcademicYear '{instance.name}' {action}d."
    )


@receiver(post_save, sender=Term)
def log_term_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    AcademicAuditLog.objects.create(
        actor=get_actor(),
        action=action,
        model_name='Term',
        record_id=instance.id,
        timestamp=now(),
        notes=f"Term '{instance.name}' for year '{instance.academic_year.name}' {action}d."
    )


@receiver(post_save, sender=AcademicEvent)
def log_event_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    AcademicAuditLog.objects.create(
        actor=get_actor(),
        action=action,
        model_name='AcademicEvent',
        record_id=instance.id,
        timestamp=now(),
        notes=f"Event '{instance.title}' {action}d."
    )


@receiver(post_save, sender=HolidayBreak)
def log_holiday_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    AcademicAuditLog.objects.create(
        actor=get_actor(),
        action=action,
        model_name='HolidayBreak',
        record_id=instance.id,
        timestamp=now(),
        notes=f"Holiday '{instance.title}' {action}d."
    )


@receiver(pre_delete, sender=AcademicYear)
@receiver(pre_delete, sender=Term)
@receiver(pre_delete, sender=AcademicEvent)
@receiver(pre_delete, sender=HolidayBreak)
def log_deletion(sender, instance, **kwargs):
    AcademicAuditLog.objects.create(
        actor=get_actor(),
        action='delete',
        model_name=sender.__name__,
        record_id=instance.id,
        timestamp=now(),
        notes=f"{sender.__name__} '{instance}' deleted."
    )
