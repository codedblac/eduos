# timetable/pdf_generator.py

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from io import BytesIO
from django.http import HttpResponse
from .models import TimetableEntry

def _draw_timetable_table(c, width, height, title, entries, days, periods_per_day, subject_attr='subject', stream_attr='stream'):
    """
    Draw timetable table on canvas using custom days and periods per day.
    
    Parameters:
    - c: reportlab canvas
    - width, height: canvas dimensions
    - title: string title for the timetable
    - entries: queryset or list of TimetableEntry objects
    - days: list of day names, e.g. ['Monday', 'Tuesday', ...]
    - periods_per_day: int, number of periods per day
    - subject_attr: attribute name to get subject from TimetableEntry
    - stream_attr: attribute name to get stream from TimetableEntry
    """
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 2 * cm, title)

    c.setFont("Helvetica-Bold", 12)
    start_x = 3 * cm
    start_y = height - 3.5 * cm
    cell_width = (width - start_x - 2 * cm) / (len(days) + 1)
    cell_height = 1.2 * cm

    # Header row
    c.setFillColor(colors.darkblue)
    c.rect(start_x, start_y - cell_height, cell_width, cell_height, stroke=1, fill=1)
    c.setFillColor(colors.white)
    c.drawCentredString(start_x + cell_width / 2, start_y - cell_height + 4, "Period")

    for i, day in enumerate(days):
        x = start_x + cell_width * (i + 1)
        c.rect(x, start_y - cell_height, cell_width, cell_height, stroke=1, fill=1)
        c.drawCentredString(x + cell_width / 2, start_y - cell_height + 4, day)

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 8)

    # Build lookup dict {(day_of_week, period): entry}
    # Assuming TimetableEntry.day_of_week matches day names exactly
    entry_lookup = {}
    for e in entries:
        entry_lookup[(e.day_of_week, e.period)] = e

    for period in range(1, periods_per_day + 1):
        y = start_y - cell_height * (period + 1)

        # Period number column
        c.rect(start_x, y, cell_width, cell_height, stroke=1, fill=0)
        c.drawCentredString(start_x + cell_width / 2, y + 4, str(period))

        for day_idx, day in enumerate(days):
            x = start_x + cell_width * (day_idx + 1)
            c.rect(x, y, cell_width, cell_height, stroke=1, fill=0)

            entry = entry_lookup.get((day, period))
            if entry:
                subject_name = getattr(entry, subject_attr).name if getattr(entry, subject_attr) else "N/A"
                stream_name = getattr(entry, stream_attr).name if getattr(entry, stream_attr) else "N/A"
                room_name = entry.room.name if entry.room else "N/A"

                c.drawString(x + 2, y + cell_height - 10, subject_name)
                c.drawString(x + 2, y + cell_height - 22, stream_name)
                c.drawString(x + 2, y + cell_height - 34, f"Room: {room_name}")

def generate_timetable_pdf(buffer, entries, title, days, periods_per_day, subject_attr='subject', stream_attr='stream'):
    """
    Generate timetable PDF into the given buffer.

    Parameters:
    - buffer: BytesIO buffer to write PDF data
    - entries: TimetableEntry queryset or list
    - title: Title string for the PDF header
    - days: List of day names (strings)
    - periods_per_day: Int number of periods per day
    - subject_attr: string attribute name for subject in entries
    - stream_attr: string attribute name for stream in entries
    """
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    _draw_timetable_table(c, width, height, title, entries, days, periods_per_day, subject_attr, stream_attr)

    c.showPage()
    c.save()
    buffer.seek(0)

def generate_teacher_timetable_pdf(teacher, days, periods_per_day):
    """
    Generate and return HTTP response for a PDF timetable of a specific teacher.
    """
    buffer = BytesIO()
    entries = TimetableEntry.objects.filter(teacher=teacher).order_by('day_of_week', 'period')
    title = f"Timetable for Teacher: {teacher.first_name} {teacher.last_name}"

    generate_timetable_pdf(buffer, entries, title, days, periods_per_day, subject_attr='subject', stream_attr='stream')

    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"timetable_teacher_{teacher.first_name}_{teacher.last_name}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def generate_stream_timetable_pdf(stream, days, periods_per_day):
    """
    Generate and return HTTP response for a PDF timetable of a specific stream/class.
    """
    buffer = BytesIO()
    entries = TimetableEntry.objects.filter(stream=stream).order_by('day_of_week', 'period')
    title = f"Timetable for Stream: {stream.name}"

    generate_timetable_pdf(buffer, entries, title, days, periods_per_day, subject_attr='subject', stream_attr='stream')

    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"timetable_stream_{stream.name}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
