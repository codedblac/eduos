from datetime import date
from django.db.models import Count, F, ExpressionWrapper, DurationField
from django.db.models.functions import Cast
from .models import AcademicYear, Term, AcademicEvent, HolidayBreak


def academic_year_distribution():
    """
    Returns number of terms and academic events per academic year.
    Useful for summary charts or annual planning.
    """
    return AcademicYear.objects.annotate(
        total_terms=Count('terms', distinct=True),
        total_events=Count('terms__events', distinct=True)
    ).values('name', 'institution__name', 'total_terms', 'total_events')


def term_statistics():
    """
    Returns duration, number of events and breaks for each term.
    Great for insights or performance dashboards.
    """
    return Term.objects.annotate(
        duration_days=ExpressionWrapper(
            F('end_date') - F('start_date'),
            output_field=DurationField()
        ),
        event_count=Count('events', distinct=True),
        break_count=Count('breaks', distinct=True)
    ).values(
        'name',
        'academic_year__name',
        'start_date',
        'end_date',
        'duration_days',
        'event_count',
        'break_count'
    )


def active_terms_summary():
    """
    Returns a list of currently running terms with days remaining.
    Ideal for alerts, dashboard cards, or monitoring UI.
    """
    today = date.today()
    terms = Term.objects.filter(start_date__lte=today, end_date__gte=today)

    return [
        {
            'term': term.name,
            'academic_year': term.academic_year.name,
            'start_date': term.start_date,
            'end_date': term.end_date,
            'days_remaining': (term.end_date - today).days
        }
        for term in terms
    ]


def event_distribution_by_term():
    """
    Groups academic events per term for bar/pie chart analytics.
    """
    return AcademicEvent.objects.values(
        'term__name',
        'term__academic_year__name'
    ).annotate(
        total_events=Count('id')
    ).order_by('-total_events')


def holiday_summary():
    """
    Lists upcoming holidays with start and end dates.
    Useful for calendar integration or upcoming reminders.
    """
    today = date.today()
    return HolidayBreak.objects.filter(end_date__gte=today).values(
        'title',
        'start_date',
        'end_date',
        'term__name',
        'term__academic_year__name'
    ).order_by('start_date')
