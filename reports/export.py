import tempfile
from django.http import FileResponse
from weasyprint import HTML
from django.template.loader import render_to_string


def export_report_to_pdf(report):
    html_string = render_to_string('reports/pdf_template.html', {'report': report})
    html = HTML(string=html_string)
    pdf_file = tempfile.NamedTemporaryFile(delete=True, suffix=".pdf")
    html.write_pdf(target=pdf_file.name)

    return FileResponse(open(pdf_file.name, 'rb'), content_type='application/pdf')


def export_report_to_excel(report):
    import pandas as pd
    from io import BytesIO
    from django.core.files.base import ContentFile

    student_data = [{
        'Student': perf.student.full_name,
        'Grade': perf.grade,
        'Mean Score': perf.mean_score,
        'Rank': perf.rank
    } for perf in report.student_performances.all()]

    df = pd.DataFrame(student_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Performance')

    return ContentFile(output.getvalue(), name=f'{report.title}.xlsx')
