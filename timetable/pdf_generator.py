from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from io import BytesIO
from django.http import HttpResponse

from .models import TimetableEntry, PeriodTemplate


def _draw_timetable_table(c, width, height, title, entries, periods):
    """
    Draws a timetable as a grid with days as columns and periods as rows.
    """
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 2 * cm, title)

    days = sorted(set(p.day for p in periods))
    start_x = 3 * cm
    start_y = height - 3.5 * cm
    cell_width = (width - start_x - 2 * cm) / (len(days) + 1)
    cell_height = 1.5 * cm

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.darkblue)

    # Header row
    c.rect(start_x, start_y - cell_height, cell_width, cell_height, fill=1)
    c.setFillColor(colors.white)
    c.drawCentredString(start_x + cell_width / 2, start_y - cell_height + 4, "Time")

    for i, day in enumerate(days):
        x = start_x + cell_width * (i + 1)
        c.rect(x, start_y - cell_height, cell_width, cell_height, fill=1)
        c.drawCentredString(x + cell_width / 2, start_y - cell_height + 4, day)

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)

    sorted_periods = sorted(periods, key=lambda p: (p.day, p.start_time))
    for row_idx, period in enumerate(sorted_periods):
        y = start_y - cell_height * (row_idx + 2)

        # Time label column
        c.rect(start_x, y, cell_width, cell_height, stroke=1, fill=0)
        time_range = f"{period.start_time.strftime('%H:%M')} - {period.end_time.strftime('%H:%M')}"
        c.drawCentredString(start_x + cell_width / 2, y + 4, time_range)

        for col_idx, day in enumerate(days):
            x = start_x + cell_width * (col_idx + 1)
            c.rect(x, y, cell_width, cell_height, stroke=1, fill=0)

            entry = entries.filter(period_template=period, period_template__day=day).first()
            if entry:
                subject = entry.subject.name
                stream = entry.stream.name
                teacher = entry.teacher.user.get_full_name()
                room = entry.room.name if entry.room else "N/A"

                lines = [subject, stream, teacher, f"Room: {room}"]
                for i, line in enumerate(lines):
                    c.drawString(x + 2, y + cell_height - (10 + i * 10), line)


def generate_timetable_pdf(buffer, entries, title, periods):
    """
    Generates the PDF of timetable using the canvas and writes to buffer.
    """
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    _draw_timetable_table(c, width, height, title, entries, periods)
    c.showPage()
    c.save()
    buffer.seek(0)


def generate_teacher_timetable_pdf(teacher):
    """
    Return PDF response for a teacher's timetable.
    """
    buffer = BytesIO()
    entries = TimetableEntry.objects.filter(teacher=teacher).select_related(
        'period_template', 'subject', 'stream', 'room'
    )
    periods = PeriodTemplate.objects.filter(
        class_level__streams__teachers=teacher
    ).distinct()

    title = f"Teacher Timetable: {teacher.user.get_full_name()}"
    generate_timetable_pdf(buffer, entries, title, periods)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="timetable_teacher_{teacher.id}.pdf"'
    return response


def generate_stream_timetable_pdf(stream):
    """
    Return PDF response for a class stream's timetable.
    """
    buffer = BytesIO()
    entries = TimetableEntry.objects.filter(stream=stream).select_related(
        'period_template', 'subject', 'teacher', 'room'
    )
    periods = PeriodTemplate.objects.filter(
        class_level=stream.class_level
    ).distinct()

    title = f"Class Timetable: {stream.name}"
    generate_timetable_pdf(buffer, entries, title, periods)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="timetable_stream_{stream.name}.pdf"'
    return response
