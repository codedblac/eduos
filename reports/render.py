from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML
from io import BytesIO

from .models import GeneratedReport
from .ai import detect_at_risk_students, suggest_actions_for_student


def render_report_context(report: GeneratedReport) -> dict:
    """
    Prepares all context data needed for rendering PDFs or frontend views.
    """
    student_performances = report.student_performances.select_related('student', 'stream')
    subject_breakdowns = report.subject_breakdowns.select_related('subject', 'teacher')

    at_risk = detect_at_risk_students(report)
    at_risk_suggestions = {
        perf.student.id: suggest_actions_for_student(perf)
        for perf in at_risk
    }

    return {
        "report": report,
        "institution": report.institution,
        "generated_by": report.generated_by.get_full_name() if report.generated_by else "System",
        "date_generated": timezone.localtime(report.date_generated).strftime('%d %b %Y'),
        "students": student_performances,
        "subjects": subject_breakdowns,
    
        "ai_flags": report.smart_flags or {},
        "at_risk_suggestions": at_risk_suggestions,
    }


def render_report_as_html(report: GeneratedReport) -> str:
    """
    Renders the report into an HTML string using a template.
    """
    context = render_report_context(report)
    return render_to_string('reports/pdf_template.html', context)


def render_report_as_pdf(report: GeneratedReport) -> BytesIO:
    """
    Generates a PDF file object for the given report.
    """
    html_string = render_report_as_html(report)
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    pdf_file.seek(0)
    return pdf_file


def render_report_for_mobile(report: GeneratedReport) -> dict:
    """
    JSON-style representation for API/mobile frontend.
    """
    context = render_report_context(report)

    return {
        "title": report.title,
        "term": report.term,
        "year": report.year,
        "generated_by": context["generated_by"],
        "students": [
            {
                "name": sp.student.full_name,
                "mean_score": sp.mean_score,
                "grade": sp.grade,
                "rank": sp.rank,
                "remedial_suggestion": sp.remedial_suggestion,
                "flagged": sp.flagged
            }
            for sp in context["students"]
        ],
        "subjects": [
            {
                "subject": sb.subject.name,
                "teacher": sb.teacher.get_full_name() if sb.teacher else None,
                "average_score": sb.average_score,
                "pass_rate": sb.pass_rate,
                "failure_rate": sb.failure_rate,
                "comment": sb.comment
            }
            for sb in context["subjects"]
        ],
        "flags": context["ai_flags"],
        "at_risk_notes": context["at_risk_suggestions"]
    }
