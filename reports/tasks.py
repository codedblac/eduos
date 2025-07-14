import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from institutions.models import Institution
from classes.models import ClassLevel, Stream
from accounts.models import CustomUser
from .models import GeneratedReport
from .ai import detect_at_risk_students, suggest_actions_for_student
from .export import export_report_to_pdf, export_report_to_excel
from notifications.utils import send_notification

# Import your report generator utility
from .utils import generate_student_academic_summary

logger = logging.getLogger(__name__)


@shared_task
def generate_academic_report_task(term, year, class_level_id, stream_id, institution_id, generated_by_id=None):
    """
    Generates and saves a full academic report.
    """
    try:
        institution = Institution.objects.get(id=institution_id)
        class_level = ClassLevel.objects.get(id=class_level_id)
        stream = Stream.objects.get(id=stream_id)
        generated_by = CustomUser.objects.get(id=generated_by_id) if generated_by_id else None

        report = generate_student_academic_summary(
            term=term,
            year=year,
            class_level=class_level,
            stream=stream,
            institution=institution,
            generated_by=generated_by
        )

        return {"status": "success", "report_id": report.id}

    except ObjectDoesNotExist as e:
        logger.error(f"Missing object during report generation: {e}")
        return {"status": "error", "message": f"Object not found: {str(e)}"}

    except Exception as e:
        logger.exception("Unexpected error during report generation")
        return {"status": "error", "message": str(e)}


@shared_task
def run_ai_analysis_on_report(report_id):
    """
    Runs AI-based risk analysis and sends guardian alerts for underperformers.
    """
    try:
        report = GeneratedReport.objects.get(id=report_id)
        at_risk = detect_at_risk_students(report)
        alert_count = 0

        for perf in at_risk:
            action = suggest_actions_for_student(perf)

            guardian_user = getattr(getattr(perf.student, "guardian_user", None), "user", None)
            if guardian_user:
                send_notification(
                    user=guardian_user,
                    title="Academic Risk Alert",
                    message=(
                        f"{perf.student.full_name} has been flagged as academically at-risk "
                        f"in {report.title}. Suggested intervention: {action}"
                    ),
                    category="academic",
                    institution=report.institution
                )
                alert_count += 1

        return {"status": "success", "at_risk_alerts_sent": alert_count}

    except GeneratedReport.DoesNotExist:
        logger.error(f"Report with ID {report_id} not found for AI analysis.")
        return {"status": "error", "message": "Report not found"}

    except Exception as e:
        logger.exception("Error during AI risk analysis task")
        return {"status": "error", "message": str(e)}


@shared_task
def export_report_as_pdf(report_id):
    """
    Generates and stores a PDF version of the report.
    """
    try:
        report = GeneratedReport.objects.get(id=report_id)
        return export_report_to_pdf(report)

    except GeneratedReport.DoesNotExist:
        logger.error(f"Report not found for PDF export: ID {report_id}")
        return None

    except Exception as e:
        logger.exception("Failed to export report as PDF")
        return None


@shared_task
def export_report_as_excel(report_id):
    """
    Generates and stores an Excel version of the report.
    """
    try:
        report = GeneratedReport.objects.get(id=report_id)
        return export_report_to_excel(report)

    except GeneratedReport.DoesNotExist:
        logger.error(f"Report not found for Excel export: ID {report_id}")
        return None

    except Exception as e:
        logger.exception("Failed to export report as Excel")
        return None


@shared_task
def notify_top_performers(report_id, top_n=5):
    """
    Notifies guardians of top-performing students.
    """
    try:
        report = GeneratedReport.objects.get(id=report_id)
        top_students = report.student_performances.order_by('-mean_score')[:top_n]
        sent_count = 0

        for perf in top_students:
            guardian_user = getattr(getattr(perf.student, "guardian_user", None), "user", None)
            if guardian_user:
                send_notification(
                    user=guardian_user,
                    title="🎉 Top Performer Alert",
                    message=(
                        f"Congratulations! {perf.student.full_name} ranked #{perf.rank} "
                        f"in {report.title}. Keep up the great work!"
                    ),
                    category="academic",
                    institution=report.institution
                )
                sent_count += 1

        return {"status": "success", "top_performer_notifications": sent_count}

    except GeneratedReport.DoesNotExist:
        logger.error(f"Report not found for top performer notifications: ID {report_id}")
        return {"status": "error", "message": "Report not found"}

    except Exception as e:
        logger.exception("Failed to send top performer notifications")
        return {"status": "error", "message": str(e)}
