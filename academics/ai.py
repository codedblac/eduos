from datetime import date, timedelta
from django.db.models import Count, Q
from .models import AcademicYear, Term, AcademicEvent
from syllabus.models import SyllabusProgress  # if available
from timetable.models import TimetableEntry  # if integrated


class AcademicAIEngine:

    @staticmethod
    def predict_term_progress(term: Term):
        """Estimate topic coverage progress rate based on time elapsed"""
        today = date.today()
        total_days = (term.end_date - term.start_date).days
        days_elapsed = (today - term.start_date).days
        elapsed_ratio = max(0, min(days_elapsed / total_days, 1))

        return round(elapsed_ratio * 100, 1)

    @staticmethod
    def detect_term_conflicts(term: Term):
        """Detect overlapping academic events or scheduling conflicts"""
        conflicts = AcademicEvent.objects.filter(
            term=term,
            start_date__lte=term.end_date,
            end_date__gte=term.start_date,
        ).annotate(
            duration=Count('start_date')
        ).order_by('start_date')
        return conflicts

    @staticmethod
    def generate_term_summary(term: Term):
        """Return insights about number of events, weeks left, progress %"""
        today = date.today()
        total_days = (term.end_date - term.start_date).days
        days_left = (term.end_date - today).days if today <= term.end_date else 0

        event_count = AcademicEvent.objects.filter(term=term).count()
        percent_time_elapsed = AcademicAIEngine.predict_term_progress(term)

        return {
            "term": term.name,
            "academic_year": term.academic_year.name,
            "weeks_remaining": days_left // 7,
            "event_count": event_count,
            "time_elapsed_percent": percent_time_elapsed,
        }

    @staticmethod
    def detect_syllabus_gap(term: Term):
        """Detect subjects that are not progressing as expected"""
        try:
            progress = SyllabusProgress.objects.filter(term=term)
            stalled = progress.filter(status='pending')
            return stalled.values('subject__name', 'class_level__name', 'teacher__full_name')
        except Exception:
            return []

    @staticmethod
    def suggest_schedule_adjustments(term: Term):
        """Based on syllabus lag or event density, recommend changes"""
        conflicts = AcademicAIEngine.detect_term_conflicts(term)
        if conflicts.count() > 5:
            return "Too many academic events — consider adjusting teaching days."

        progress = AcademicAIEngine.predict_term_progress(term)
        if progress > 90:
            return "Term is nearly over. Ensure all assessments and syllabus coverage are complete."

        return "Schedule within acceptable range. Monitor syllabus pace."
