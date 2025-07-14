import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import GeneratedReport
from .tasks import (
    run_ai_analysis_on_report,
    export_report_as_pdf,
    export_report_as_excel,
    notify_top_performers,
)
from notifications.utils import send_notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=GeneratedReport)
def handle_new_report(sender, instance, created, **kwargs):
    """
    Post-save hook for GeneratedReport.

    Triggers:
    - AI analysis of report data
    - PDF and Excel export tasks
    - Top performers notification
    - Notification to the report generator
    """

    if not created:
        return  # Only run on creation

    def trigger_report_tasks():
        try:
            logger.info(f"[REPORTS] Triggering tasks for GeneratedReport ID {instance.id}")

            # 1. AI risk analysis
            run_ai_analysis_on_report.delay(instance.id)
            logger.info(f"[REPORTS] Queued AI analysis task for report {instance.id}")

            # 2. Export to PDF
            export_report_as_pdf.delay(instance.id)
            logger.info(f"[REPORTS] Queued PDF export task for report {instance.id}")

            # 3. Export to Excel
            export_report_as_excel.delay(instance.id)
            logger.info(f"[REPORTS] Queued Excel export task for report {instance.id}")

            # 4. Notify top performers
            notify_top_performers.delay(instance.id)
            logger.info(f"[REPORTS] Queued top performer notifications for report {instance.id}")

            # 5. Notify creator (if available)
            if instance.generated_by:
                send_notification(
                    user=instance.generated_by,
                    title=f"📊 Report Ready: {instance.title}",
                    message="Your academic report has been successfully generated and exported.",
                    category="reports",
                    institution=instance.institution
                )
                logger.info(f"[REPORTS] Notification sent to report creator {instance.generated_by}")

        except Exception as e:
            logger.exception(f"[REPORTS] Error in post-save for report ID {instance.id}: {str(e)}")

    # Use on_commit to ensure signal fires after transaction is committed
    transaction.on_commit(trigger_report_tasks)
