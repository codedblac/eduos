from django.db.models import Count, Avg, Q, F, DateField
from django.db.models.functions import TruncDate
from django.utils import timezone
from .models import Applicant, EntranceExam, AdmissionSession


def get_admission_summary():
    """
    Returns a dictionary of high-level admission metrics.
    """
    today = timezone.now().date()
    total = Applicant.objects.count()
    return {
        "total_applicants": total,
        "submitted_today": Applicant.objects.filter(submitted_on__date=today).count(),
        "shortlisted": Applicant.objects.filter(application_status="shortlisted").count(),
        "accepted": Applicant.objects.filter(application_status="accepted").count(),
        "rejected": Applicant.objects.filter(application_status="rejected").count(),
        "enrolled": Applicant.objects.filter(application_status="enrolled").count(),
        "submission_percentage_today": round(
            (Applicant.objects.filter(submitted_on__date=today).count() / total) * 100, 2
        ) if total > 0 else 0
    }


def get_gender_distribution():
    """
    Distribution of applicants by gender.
    """
    return Applicant.objects.values("gender").annotate(
        count=Count("id")
    ).order_by("-count")


def get_disability_statistics():
    """
    Number and percentage of applicants with disabilities or chronic illnesses.
    """
    total = Applicant.objects.count()
    has_disability = Applicant.objects.filter(has_disability=True).count()
    has_chronic = Applicant.objects.filter(has_chronic_illness=True).count()

    return {
        "has_disability": has_disability,
        "has_chronic_illness": has_chronic,
        "disability_pct": round((has_disability / total) * 100, 2) if total else 0,
        "chronic_pct": round((has_chronic / total) * 100, 2) if total else 0,
    }


def get_orphan_status_statistics():
    """
    Count of applicants per orphan status category.
    """
    return Applicant.objects.values("orphan_status").annotate(
        count=Count("id")
    ).order_by("-count")


def get_talents_distribution():
    """
    Count of applicants who filled in talents.
    """
    return {
        "with_talents": Applicant.objects.exclude(talents__exact="").count(),
        "without_talents": Applicant.objects.filter(Q(talents__isnull=True) | Q(talents__exact="")).count()
    }


def get_applicants_by_class_level():
    """
    Applicants grouped by their entry class level.
    """
    return Applicant.objects.values(
        class_level=F("entry_class_level__name")
    ).annotate(
        count=Count("id")
    ).order_by("class_level")


def get_average_entrance_scores():
    """
    Average entrance exam scores per class level.
    """
    return EntranceExam.objects.values(
        class_level=F("applicant__entry_class_level__name")
    ).annotate(
        average_score=Avg("score")
    ).order_by("class_level")


def get_application_trends_over_time():
    """
    Application submission trends grouped by date.
    """
    return Applicant.objects.annotate(
        date=TruncDate("submitted_on")
    ).values("date").annotate(
        count=Count("id")
    ).order_by("date")


def get_session_based_statistics(session_id):
    """
    Metrics for a specific admission session.
    """
    qs = Applicant.objects.filter(admission_session_id=session_id)
    total = qs.count()
    return {
        "total": total,
        "shortlisted": qs.filter(application_status="shortlisted").count(),
        "accepted": qs.filter(application_status="accepted").count(),
        "enrolled": qs.filter(application_status="enrolled").count(),
        "rejected": qs.filter(application_status="rejected").count(),
        "submitted_today": qs.filter(submitted_on__date=timezone.now().date()).count(),
    }


def get_special_attention_flags():
    """
    Flags applicants who may need extra review due to:
    - Top or bottom scores
    - Disability / illness / orphan status
    """
    return Applicant.objects.filter(
        Q(entranceexam__score__gte=90) |
        Q(entranceexam__score__lte=30) |
        Q(has_disability=True) |
        Q(has_chronic_illness=True) |
        Q(orphan_status__in=["partial", "full"])
    ).distinct()


def get_top_performing_applicants(limit=10):
    """
    Return top applicants by exam score.
    """
    return EntranceExam.objects.select_related("applicant").filter(score__isnull=False).order_by("-score")[:limit]


def get_geographical_distribution():
    """
    Get applicant counts by county.
    """
    return Applicant.objects.values("county").annotate(
        count=Count("id")
    ).order_by("-count")


def get_status_by_gender():
    """
    Status (pending, accepted, etc.) breakdown by gender.
    """
    return Applicant.objects.values("gender", "application_status").annotate(
        count=Count("id")
    ).order_by("gender", "application_status")


def get_admission_session_summary():
    """
    Group total, accepted, and enrolled per session.
    """
    return AdmissionSession.objects.annotate(
        total=Count("applicant"),
        accepted=Count("applicant", filter=Q(applicant__application_status="accepted")),
        enrolled=Count("applicant", filter=Q(applicant__application_status="enrolled")),
    ).values("name", "total", "accepted", "enrolled")
