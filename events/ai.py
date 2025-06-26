from django.utils import timezone
from datetime import timedelta
from events.models import Event
from exams.models import ExamSchedule
from timetable.models import TimetableEntry
from institutions.models import Holiday
from accounts.models import CustomUser


def detect_conflicts(start, end, institution, participants=[]):
    conflicts = []

    # Existing overlapping events
    existing = Event.objects.filter(
        institution=institution,
        start_time__lt=end,
        end_time__gt=start
    )
    if existing.exists():
        conflicts.append("Overlaps with another event")

    # Exams
    exams = ExamSchedule.objects.filter(
        institution=institution,
        start_time__lt=end,
        end_time__gt=start
    )
    if exams.exists():
        conflicts.append("Exam scheduled in that period")

    # Timetable blocks
    if participants:
        ids = [p.id for p in participants]
        class_blocks = TimetableEntry.objects.filter(
            institution=institution,
            teacher__in=ids,
            start_time__lt=end,
            end_time__gt=start
        )
        if class_blocks.exists():
            conflicts.append("Timetable conflict")

    # Holidays
    if Holiday.objects.filter(institution=institution, date__range=(start.date(), end.date())).exists():
        conflicts.append("Holiday conflict")

    return conflicts


def suggest_slots(institution, duration_minutes=60, participants=[], days_ahead=14, buffer_minutes=15):
    suggestions = []
    now = timezone.now()

    for day in range(1, days_ahead + 1):
        base = now + timedelta(days=day)
        for hour in range(8, 18):  # From 8 AM to 5 PM
            start = base.replace(hour=hour, minute=0, second=0, microsecond=0)
            end = start + timedelta(minutes=duration_minutes)

            if detect_conflicts(start, end, institution, participants):
                continue

            suggestions.append({
                "start_time": start,
                "end_time": end,
                "confidence": "high" if hour in [10, 14] else "medium"
            })

            if len(suggestions) >= 5:
                return suggestions

    return suggestions
