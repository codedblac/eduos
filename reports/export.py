import os
from io import BytesIO
import pandas as pd
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils.timezone import now
from .models import GeneratedReport
from .render import render_report_as_pdf


def export_report_to_pdf(report: GeneratedReport) -> str:
    """
    Renders and saves the report as a PDF file.
    Returns the path of the saved file.
    """
    pdf_file = render_report_as_pdf(report)

    filename = f"{slugify(report.title)}-{report.term}-{report.year}.pdf"
    filepath = f"reports/generated/{filename}"
    report.file.save(filepath, ContentFile(pdf_file.read()))
    return report.file.url


def export_report_to_excel(report: GeneratedReport) -> str:
    """
    Exports report data (students + subject stats) to an Excel file.
    Returns the file path.
    """
    # Student performance sheet
    student_data = []
    for perf in report.student_performances.select_related('student'):
        student_data.append({
            "Student": perf.student.full_name,
            "Total Marks": perf.total_marks,
            "Mean Score": perf.mean_score,
            "Grade": perf.grade,
            "Rank": perf.rank,
            "Out of": perf.position_out_of,
            "Stream": perf.stream.name if perf.stream else "",
            "Class": perf.class_level.name if perf.class_level else "",
            "Flagged": perf.flagged,
            "Remedial Suggestion": perf.remedial_suggestion or ""
        })

    student_df = pd.DataFrame(student_data)

    # Subject breakdown sheet
    subject_data = []
    for sb in report.subject_breakdowns.select_related('subject', 'teacher'):
        subject_data.append({
            "Subject": sb.subject.name,
            "Teacher": sb.teacher.get_full_name() if sb.teacher else "",
            "Class": sb.class_level.name if sb.class_level else "",
            "Stream": sb.stream.name if sb.stream else "",
            "Exam": str(sb.exam) if sb.exam else "",
            "Average Score": sb.average_score,
            "Top Score": sb.top_score,
            "Lowest Score": sb.lowest_score,
            "Pass Rate (%)": sb.pass_rate,
            "Failure Rate (%)": sb.failure_rate,
            "Most Common Grade": sb.most_common_grade or "",
            "Comment": sb.comment or ""
        })

    subject_df = pd.DataFrame(subject_data)

    # Excel output
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        student_df.to_excel(writer, sheet_name='Student Performance', index=False)
        subject_df.to_excel(writer, sheet_name='Subject Breakdown', index=False)

    filename = f"{slugify(report.title)}-{report.term}-{report.year}.xlsx"
    filepath = f"reports/excel/{filename}"
    report.file.save(filepath, ContentFile(output.getvalue()))
    return report.file.url
