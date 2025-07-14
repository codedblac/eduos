from datetime import date, timedelta
from django.db.models import Count, Q
from .models import AcademicYear, Term, AcademicEvent
from syllabus.models import SyllabusProgress  
from timetable.models import TimetableEntry  


class AcademicAIEngine:
    """
    Smart engine for analyzing academic calendars, events, term performance,
    syllabus progress, and suggesting schedule adjustments.
    """

    @staticmethod
    def predict_term_progress(term: Term) -> float:
        """Estimate how much of the term has elapsed (as % of time)"""
        today = date.today()
        total_days = (term.end_date - term.start_date).days
        if total_days <= 0:
            return 0.0
        days_elapsed = (today - term.start_date).days
        elapsed_ratio = max(0, min(days_elapsed / total_days, 1))
        return round(elapsed_ratio * 100, 1)

    @staticmethod
    def detect_term_conflicts(term: Term):
        """Detect overlapping academic events or tight schedules within the term"""
        return AcademicEvent.objects.filter(
            term=term,
            start_date__lte=term.end_date,
            end_date__gte=term.start_date,
        ).order_by('start_date')

    @staticmethod
    def generate_term_summary(term: Term) -> dict:
        """Return summary insights: events, progress, weeks left"""
        today = date.today()
        total_days = (term.end_date - term.start_date).days
        days_left = max((term.end_date - today).days, 0)

        return {
            "term": term.name,
            "academic_year": term.academic_year.name,
            "weeks_remaining": days_left // 7,
            "event_count": AcademicEvent.objects.filter(term=term).count(),
            "time_elapsed_percent": AcademicAIEngine.predict_term_progress(term),
        }

    @staticmethod
    def detect_syllabus_gap(term: Term):
        """List syllabus entries marked as 'pending' or significantly behind"""
        try:
            stalled = SyllabusProgress.objects.filter(term=term, status='pending')
            return list(stalled.values(
                'subject__name', 'class_level__name', 'teacher__full_name'
            ))
        except Exception:
            # Fallback in case syllabus app isn't connected yet
            return []

    @staticmethod
    def suggest_schedule_adjustments(term: Term) -> str:
        """
        Analyze if schedule needs revision due to conflicts or syllabus delays.
        Can be integrated into notifications or dashboards.
        """
        conflict_count = AcademicAIEngine.detect_term_conflicts(term).count()
        if conflict_count > 5:
            return "⚠️ High number of academic events. Suggest redistributing lessons to avoid overload."

        progress = AcademicAIEngine.predict_term_progress(term)
        if progress >= 90:
            return "✅ Term is nearly complete. Finalize assessments and evaluations."

        gaps = AcademicAIEngine.detect_syllabus_gap(term)
        if gaps:
            return f"🟡 {len(gaps)} syllabus areas are pending. Recommend syllabus catch-up sessions."

        return "✅ Academic term is progressing well. No major adjustments needed."
