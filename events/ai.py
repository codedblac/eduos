from django.utils import timezone
from datetime import timedelta
from events.models import Event
from exams.models import ExamSchedule
from timetable.models import TimetableEntry
from academics.models import HolidayBreak
from accounts.models import CustomUser


def detect_conflicts(start, end, institution, participants=None):
    """
    Detects scheduling conflicts for an event within the given time range.
    Returns a list of conflict messages.
    """
    conflicts = []

    if participants is None:
        participants = []

    # Check for overlapping events
    if Event.objects.filter(
        institution=institution,
        start_time__lt=end,
        end_time__gt=start
    ).exists():
        conflicts.append("Conflicts with another scheduled event.")

    # Check for overlapping exam schedules
    if ExamSchedule.objects.filter(
        institution=institution,
        start_time__lt=end,
        end_time__gt=start
    ).exists():
        conflicts.append("An exam is scheduled during this time.")

    # Check for timetable conflicts for participants
    if participants:
        participant_ids = [p.id for p in participants if isinstance(p, CustomUser)]
        if participant_ids:
            if TimetableEntry.objects.filter(
                institution=institution,
                teacher__in=participant_ids,
                start_time__lt=end,
                end_time__gt=start
            ).exists():
                conflicts.append("Participant has a timetable conflict.")

    # Check for holiday overlap
    if HolidayBreak.objects.filter(
        institution=institution,
        date__range=(start.date(), end.date())
    ).exists():
        conflicts.append("The date overlaps with a holiday or term break.")

    return conflicts


def suggest_slots(institution, duration_minutes=60, participants=None, days_ahead=14, buffer_minutes=15):
    """
    Suggests available time slots without conflicts, up to a limited number.
    Returns a list of dictionaries with start_time, end_time, and confidence level.
    """
    if participants is None:
        participants = []

    suggestions = []
    now = timezone.now()

    for day_offset in range(1, days_ahead + 1):
        day = now + timedelta(days=day_offset)
        for hour in range(8, 18):  # Office hours: 8 AM – 5 PM
            start = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            end = start + timedelta(minutes=duration_minutes)

            if not detect_conflicts(start, end, institution, participants):
                suggestions.append({
                    "start_time": start,
                    "end_time": end,
                    "confidence": "high" if hour in [10, 14] else "medium"
                })

            if len(suggestions) >= 5:
                return suggestions

    return suggestions
