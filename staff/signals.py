# staff/signals.py

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import StaffProfile, EmploymentHistory
from .models import Staff
from accounts.models import CustomUser
from notifications.utils import send_notification_to_user


@receiver(post_save, sender=StaffProfile)
def create_employment_history(sender, instance, created, **kwargs):
    if created:
        EmploymentHistory.objects.create(
            staff_profile=instance,
            position=instance.current_position,
            department=instance.department,
            start_date=instance.date_joined,
            employment_type=instance.employment_type,
            remarks='Auto-created on staff onboarding.'
        )

        # Notify HR
        hr_users = CustomUser.objects.filter(groups__name='HR Manager')
        for hr in hr_users:
            send_notification_to_user(
                hr,
                title="New Staff Profile Added",
                message=f"{instance.user.get_full_name()} has been added to staff as {instance.current_position}."
            )


@receiver(post_save, sender=StaffProfile)
def update_employment_history(sender, instance, created, **kwargs):
    if not created:
        # Ensure active employment history is in sync
        try:
            latest_record = EmploymentHistory.objects.filter(staff_profile=instance).latest('start_date')
            if latest_record.position != instance.current_position or latest_record.department != instance.department:
                EmploymentHistory.objects.create(
                    staff_profile=instance,
                    position=instance.current_position,
                    department=instance.department,
                    start_date=now().date(),
                    employment_type=instance.employment_type,
                    remarks='Updated due to role or department change.'
                )
        except EmploymentHistory.DoesNotExist:
            # Handle orphaned staff without history
            EmploymentHistory.objects.create(
                staff_profile=instance,
                position=instance.current_position,
                department=instance.department,
                start_date=instance.date_joined,
                employment_type=instance.employment_type,
                remarks='Auto-created recovery history.'
            )


@receiver(pre_delete, sender=StaffProfile)
def archive_staff_on_delete(sender, instance, **kwargs):
    """
    When a staff profile is deleted, we archive the history and notify HR.
    """
    EmploymentHistory.objects.create(
        staff_profile=instance,
        position=instance.current_position,
        department=instance.department,
        start_date=instance.date_joined,
        end_date=now().date(),
        employment_type=instance.employment_type,
        remarks='Auto-archived on staff deletion.'
    )

    hr_users = CustomUser.objects.filter(groups__name='HR Manager')
    for hr in hr_users:
        send_notification_to_user(
            hr,
            title="Staff Profile Archived",
            message=f"{instance.user.get_full_name()} has been removed from active staff and archived."
        )
