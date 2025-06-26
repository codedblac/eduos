from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    VisitorLog,
    Appointment,
    ParcelDelivery,
    FrontDeskTicket,
    GatePass
)


@receiver(post_save, sender=VisitorLog)
def notify_security_on_visitor_checkin(sender, instance, created, **kwargs):
    if created:
        # Optional: Notify security or front desk via email or internal system
        print(f"[INFO] New visitor checked in: {instance.visitor_name}")


@receiver(post_save, sender=Appointment)
def notify_staff_on_appointment_created(sender, instance, created, **kwargs):
    if created and instance.meeting_with.email:
        send_mail(
            subject="New Appointment Scheduled",
            message=f"You have a scheduled appointment with {instance.visitor_name} on {instance.meeting_date} at {instance.meeting_time}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.meeting_with.email],
        )


@receiver(post_save, sender=ParcelDelivery)
def alert_recipient_on_parcel(sender, instance, created, **kwargs):
    if created and instance.recipient_type == 'student' and instance.student and instance.student.guardian_set.exists():
        for guardian in instance.student.guardian_set.all():
            # Optional: use internal notification system or SMS
            print(f"[ALERT] Parcel for {instance.student.full_name()} has arrived.")


@receiver(post_save, sender=FrontDeskTicket)
def auto_escalate_high_priority_ticket(sender, instance, **kwargs):
    if instance.priority == 'high' and instance.status == 'pending':
        # Optional: escalate to admin or notify supervisors
        print(f"[TICKET] High priority ticket submitted by {instance.submitted_by}. Needs review.")


@receiver(pre_save, sender=GatePass)
def auto_set_exit_time_on_approval(sender, instance, **kwargs):
    if instance.status == 'approved' and not instance.exit_time:
        instance.exit_time = now()
