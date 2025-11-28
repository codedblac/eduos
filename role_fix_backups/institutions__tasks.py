from celery import shared_task
from django.utils import timezone
from institutions.models import Institution, SchoolAccount
import logging

logger = logging.getLogger(__name__)

# =============================
# 📨 Welcome Email Task
# =============================

@shared_task
def send_institution_welcome_email(institution_id):
    """
    Sends a welcome email to the newly created institution's official email.
    """
    try:
        institution = Institution.objects.get(id=institution_id)
        if institution.email:
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
            logger.info(f"[Welcome Email] Sent to {institution.email}")
        else:
            logger.warning(f"[Welcome Email] Institution {institution.name} has no email set.")
    except Institution.DoesNotExist:
        logger.error(f"[Welcome Email] Institution with id={institution_id} does not exist.")

# =============================
# ⏳ Deactivate Inactive Institutions
# =============================

@shared_task
def deactivate_inactive_institutions():
    """
    Scheduled task to deactivate institutions with no activity for 1 year.
    """
    one_year_ago = timezone.now() - timezone.timedelta(days=365)
    inactive_institutions = Institution.objects.filter(
        updated_at__lt=one_year_ago,
        extra_info__isnull=True  # Optional: skip active/engaged institutions
    )
    for institution in inactive_institutions:
        if getattr(institution, 'is_active', True):
            institution.is_active = False
            institution.save(update_fields = ['is_active'])
            logger.info(f"[Deactivate] Institution deactivated due to inactivity: {institution.name}")

# =============================
# 🔄 Sync / Audit School Accounts
# =============================

@shared_task
def sync_school_account_data():
    """
    Background task to audit or sync school accounts with external systems.
    """
    accounts = SchoolAccount.objects.select_related("institution").all()
    for account in accounts:
        # Placeholder for sync or validation logic
        logger.info(f"[School Account Audit] {account.account_name} for {account.institution.name}")
        # TODO: Extend with API sync, validation, or notifications
