# admissions/analytics.py

from django.db.models import Count, Avg, Q, F
from .models import Applicant, EntranceExam, AdmissionSession
from django.utils import timezone



def get_admission_summary():
    """
    Returns a dictionary of high-level admission metrics.
    """
    return {
        "total_applicants": Applicant.objects.count(),
        "submitted_today": Applicant.objects.filter(submitted_on__date__exact=timezone.now().date()).count(),
        "shortlisted": Applicant.objects.filter(application_status="shortlisted").count(),
        "accepted": Applicant.objects.filter(application_status="accepted").count(),
        "enrolled": Applicant.objects.filter(application_status="enrolled").count(),
        "rejected": Applicant.objects.filter(application_status="rejected").count(),
    }


def get_gender_distribution():
    """
    Returns the distribution of applicants by gender.
    """
    return Applicant.objects.values("gender").annotate(count=Count("id")).order_by("-count")


def get_disability_statistics():
    """
    Number of applicants with special needs.
    """
    return {
        "has_disability": Applicant.objects.filter(has_disability=True).count(),
        "has_chronic_illness": Applicant.objects.filter(has_chronic_illness=True).count(),
    }


def get_orphan_status_statistics():
    """
    Returns how many applicants fall into each orphan category.
    """
    return Applicant.objects.values("orphan_status").annotate(count=Count("id")).order_by("-count")


def get_talents_distribution():
    """
    Tallies applicants who submitted talents.
    """
    return Applicant.objects.exclude(talents__exact="").count()


def get_applicants_by_class_level():
    """
    Returns number of applicants grouped by entry class level.
    """
    return Applicant.objects.values(class_level=F("entry_class_level__name")).annotate(count=Count("id")).order_by("class_level")


def get_average_entrance_scores():
    """
    Returns average entrance scores by session or class level.
    """
    return EntranceExam.objects.values("applicant__entry_class_level__name").annotate(
        average_score=Avg("score")
    ).order_by("applicant__entry_class_level__name")


def get_application_trends_over_time():
    """
    Returns application trends by date for graphing.
    """
    return Applicant.objects.extra(select={"date": "date(submitted_on)"}).values("date").annotate(count=Count("id")).order_by("date")


def get_session_based_statistics(session_id):
    """
    Returns stats scoped to a specific AdmissionSession.
    """
    return {
        "total": Applicant.objects.filter(admission_session_id=session_id).count(),
        "shortlisted": Applicant.objects.filter(admission_session_id=session_id, application_status="shortlisted").count(),
        "enrolled": Applicant.objects.filter(admission_session_id=session_id, application_status="enrolled").count(),
    }


def get_special_attention_flags():
    """
    Flags applicants who need special attention:
    - Very high or very low entrance scores
    - Disability
    - Chronic illness
    - Orphaned
    """
    return Applicant.objects.filter(
        Q(entranceexam__score__gte=90) |
        Q(entranceexam__score__lte=30) |
        Q(has_disability=True) |
        Q(has_chronic_illness=True) |
        Q(orphan_status__in=["partial", "full"])
    ).distinct()
