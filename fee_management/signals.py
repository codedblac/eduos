from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Payment, Invoice, RefundRequest, Penalty
from .tasks import generate_digital_receipts
from notifications.utils import notify_user


@receiver(post_save, sender=Payment)
def auto_generate_receipt(sender, instance, created, **kwargs):
    if created:
        # Task handles all unprocessed payments
        generate_digital_receipts.delay()


@receiver(post_save, sender=Invoice)
def handle_invoice_status(sender, instance, **kwargs):
    """Auto-flag overdue invoice and apply penalty if needed."""
    today = timezone.now().date()

    if instance.due_date and today > instance.due_date:
        if instance.status in ['draft', 'issued'] and not instance.is_paid:
            instance.status = 'overdue'
            instance.save(update_fields=['status'])

        # Apply penalty if not already applied
        if not Penalty.objects.filter(student=instance.student, term=instance.term, waived=False).exists():
            Penalty.objects.create(
                student=instance.student,
                term=instance.term,
                amount=100.00,  # Can make dynamic
                reason="Auto penalty for overdue invoice",
                applied_at=timezone.now()
            )


@receiver(post_save, sender=RefundRequest)
def notify_refund_status_change(sender, instance, created, **kwargs):
    """Notify guardians when refund is approved or rejected."""
    if not created and instance.status in ['approved', 'rejected']:
        user = getattr(instance.student, 'guardian_user', None)
        if user:
            notify_user(
                user=user,
                title=f"Refund {instance.status.capitalize()}",
                message=f"Refund request for {instance.student.full_name()} was {instance.status}."
            )
