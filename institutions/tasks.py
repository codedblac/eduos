from celery import shared_task
from django.utils import timezone
from institutions.models import Institution, SchoolAccount
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_institution_welcome_email(institution_id):
    """
    Sends a welcome email to the newly created institution's official email.
    """
    try:
        institution = Institution.objects.get(id=institution_id)
        if institution.email:
            # Replace with real email logic or HTML template rendering
            subject = f"Welcome to EduOS, {institution.name}"
            message = f"""
                Dear {institution.name},

                Welcome to EduOS. Your account has been created with the following code: {institution.code}.

                Please log in to configure your setup.

                Regards,
                EduOS Support Team
            """
            from django.core.mail import send_mail
            send_mail(
                subject,
                message,
                "noreply@eduos.app",
                [institution.email],
                fail_silently=False
            )
            logger.info(f"Welcome email sent to {institution.email}")
        else:
            logger.warning(f"Institution {institution.name} has no email set.")
    except Institution.DoesNotExist:
        logger.error(f"Institution with id={institution_id} does not exist.")


@shared_task
def deactivate_inactive_institutions():
    """
    Scheduled task to deactivate institutions with no activity for 1 year.
    """
    one_year_ago = timezone.now() - timezone.timedelta(days=365)
    inactive_institutions = Institution.objects.filter(
        updated_at__lt=one_year_ago,
    )
    for institution in inactive_institutions:
        institution.is_active = False
        institution.save()
        logger.info(f"Deactivated institution due to inactivity: {institution.name}")


@shared_task
def sync_school_account_data():
    """
    Example background sync or audit task for school accounts.
    This can be extended to sync with external accounting or payment APIs.
    """
    accounts = SchoolAccount.objects.select_related("institution").all()
    for account in accounts:
        # Simulate sync or audit
        logger.info(f"Auditing account: {account.account_name} for {account.institution.name}")
        # Extend: sync with payment providers, validate details, notify mismatches, etc.
