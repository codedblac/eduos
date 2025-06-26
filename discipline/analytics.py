from .models import DisciplineCase
from django.db.models import Count
from django.utils.timezone import now, timedelta


def case_count_by_severity(institution):
    return DisciplineCase.objects.filter(
        institution=institution
    ).values('severity').annotate(count=Count('id')).order_by('-count')


def top_disciplined_students(institution, limit=5):
    return DisciplineCase.objects.filter(
        institution=institution
    ).values('student__id', 'student__user__first_name', 'student__user__last_name')\
     .annotate(case_count=Count('id')).order_by('-case_count')[:limit]


def discipline_cases_trend(institution, days=30):
    start_date = now().date() - timedelta(days=days)
    return DisciplineCase.objects.filter(
        institution=institution,
        incident_date__gte=start_date
    ).values('incident_date').annotate(
        count=Count('id')
    ).order_by('incident_date')


def category_frequency(institution):
    return DisciplineCase.objects.filter(
        institution=institution
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')


def case_status_breakdown(institution):
    return DisciplineCase.objects.filter(
        institution=institution
    ).values('status').annotate(
        count=Count('id')
    ).order_by('-count')
