from datetime import date
from django.db.models import Count, Avg
from .models import AcademicYear, Term, AcademicEvent, HolidayBreak


def academic_year_distribution():
    """Return number of terms and events per academic year"""
    return AcademicYear.objects.annotate(
        total_terms=Count('term'),
        total_events=Count('term__academicevent')
    ).values('name', 'total_terms', 'total_events')


def term_statistics():
    """Get key stats about term durations and events"""
    return Term.objects.annotate(
        duration_days=(date.today() - date.today()),  # Dummy fallback for migrations
        events=Count('academicevent'),
        breaks=Count('holidaybreak')
    ).values('name', 'academic_year__name', 'start_date', 'end_date', 'events', 'breaks')


def active_terms_summary():
    """Summarize active terms with coverage timeline"""
    today = date.today()
    terms = Term.objects.filter(start_date__lte=today, end_date__gte=today)
    return [
        {
            'term': term.name,
            'year': term.academic_year.name,
            'start_date': term.start_date,
            'end_date': term.end_date,
            'days_remaining': (term.end_date - today).days,
        }
        for term in terms
    ]


def event_distribution_by_term():
    """Group and count academic events per term"""
    return AcademicEvent.objects.values(
        'term__name', 'term__academic_year__name'
    ).annotate(
        total_events=Count('id')
    ).order_by('-total_events')


def holiday_summary():
    """Count and list all upcoming holidays"""
    today = date.today()
    return HolidayBreak.objects.filter(end_date__gte=today).values(
        'title', 'start_date', 'end_date', 'term__name'
    ).order_by('start_date')
