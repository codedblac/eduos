from celery import shared_task
from institutions.models import Institution
from classes.models import ClassLevel, Stream
from accounts.models import CustomUser
from .utils.generate_academic_report import generate_academic_report
from .ai import detect_at_risk_students, suggest_actions_for_student
from .export import export_report_to_pdf, export_report_to_excel
from .models import GeneratedReport
from notifications.utils import send_notification


@shared_task
def generate_academic_report_task(term, year, class_level_id, stream_id, institution_id, generated_by_id=None):
    try:
        institution = Institution.objects.get(id=institution_id)
        class_level = ClassLevel.objects.get(id=class_level_id)
        stream = Stream.objects.get(id=stream_id)
        generated_by = CustomUser.objects.get(id=generated_by_id) if generated_by_id else None

        report = generate_academic_report(
            term=term,
            year=year,
            class_level=class_level,
            stream=stream,
            institution=institution,
            generated_by=generated_by
        )

        return {"status": "success", "report_id": report.id}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task
def run_ai_analysis_on_report(report_id):
    try:
        report = GeneratedReport.objects.get(id=report_id)
        at_risk = detect_at_risk_students(report)

        for student_perf in at_risk:
            action = suggest_actions_for_student(student_perf)

            # Send notification to guardians
            send_notification(
                user=student_perf.student.guardian_user,  # Assuming reverse relation
                title="Student Performance Alert",
                message=f"{student_perf.student.full_name} flagged as at-risk. Suggested action: {action}",
                category="academic",
                institution=report.institution
            )

        return {"status": "success", "at_risk_count": at_risk.count()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task
def export_report_as_pdf(report_id):
    try:
        report = GeneratedReport.objects.get(id=report_id)
        return export_report_to_pdf(report)
    except Exception as e:
        return None


@shared_task
def export_report_as_excel(report_id):
    try:
        report = GeneratedReport.objects.get(id=report_id)
        return export_report_to_excel(report)
    except Exception as e:
        return None


@shared_task
def notify_top_performers(report_id, top_n=5):
    try:
        report = GeneratedReport.objects.get(id=report_id)
        top_students = report.student_performances.order_by('-mean_score')[:top_n]

        for student_perf in top_students:
            send_notification(
                user=student_perf.student.guardian_user,
                title="Top Performer!",
                message=f"Congratulations! {student_perf.student.full_name} ranked #{student_perf.rank} in {report.title}",
                category="academic",
                institution=report.institution
            )

        return {"status": "success", "count": top_students.count()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
