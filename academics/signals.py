from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now

from .models import AcademicYear, Term, AcademicEvent, HolidayBreak, AcademicAuditLog
from accounts.models import CustomUser


#  Placeholder: Enhance this via middleware/thread-local context in production
def get_actor():
    """
    Return the user responsible for the action.
    Should be overridden in production with request-based context.
    """
    return None


def log_audit(action: str, instance, model_name: str, notes: str = ''):
    """
    Create an audit log entry.
    """
    AcademicAuditLog.objects.create(
        actor=get_actor(),
        action=action,
        model_name=model_name,
        record_id=instance.id,
        timestamp=now(),
        notes=notes
    )


#  Post-save Signals
@receiver(post_save, sender=AcademicYear)
def log_academic_year_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    log_audit(
        action,
        instance,
        'AcademicYear',
        f"Academic Year '{instance.name}' {action}d."
    )


@receiver(post_save, sender=Term)
def log_term_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    log_audit(
        action,
        instance,
        'Term',
        f"Term '{instance.name}' for year '{instance.academic_year.name}' {action}d."
    )


@receiver(post_save, sender=AcademicEvent)
def log_event_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    log_audit(
        action,
        instance,
        'AcademicEvent',
        f"Academic Event '{instance.title}' {action}d."
    )


@receiver(post_save, sender=HolidayBreak)
def log_holiday_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    log_audit(
        action,
        instance,
        'HolidayBreak',
        f"Holiday Break '{instance.title}' {action}d."
    )


#  Pre-delete Signals
@receiver(pre_delete, sender=AcademicYear)
@receiver(pre_delete, sender=Term)
@receiver(pre_delete, sender=AcademicEvent)
@receiver(pre_delete, sender=HolidayBreak)
def log_deletion(sender, instance, **kwargs):
    log_audit(
        action='delete',
        instance=instance,
        model_name=sender.__name__,
        notes=f"{sender.__name__} '{instance}' deleted."
    )
