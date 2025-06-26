# admissions/ai.py

import random
from datetime import timedelta
from django.utils import timezone
from .models import Applicant, EntranceExam, AdmissionOffer, AdmissionSession
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
import io
from weasyprint import HTML


def suggest_admission_offer(applicant):
    """
    Basic rule-based logic to suggest whether to offer admission to an applicant.
    Can be replaced/enhanced by ML model in future.
    """
    if hasattr(applicant, 'entranceexam'):
        exam = applicant.entranceexam
        if exam.passed and exam.score and exam.score >= 50:
            return True
    return False


def predict_success_probability(applicant):
    """
    AI-powered future performance prediction stub.
    You can later train this using historical student data.
    """
    base = 0.5  # baseline chance
    score = getattr(applicant.entranceexam, 'score', None)

    if score is not None:
        base += (float(score) - 50) / 100  # adjust by score offset

    if applicant.has_disability or applicant.has_chronic_illness:
        base -= 0.1  # minor deduction for potential support needs

    # Add talent as a positive boost
    if applicant.talents:
        base += 0.05

    return round(min(max(base, 0), 1), 2)  # clamp between 0 and 1


def recommend_class_allocation(applicant, available_classes):
    """
    Recommends the best class for applicant based on even distribution logic.
    """
    # Count current students per class
    class_distribution = {cls.id: cls.student_set.count() for cls in available_classes}
    recommended_class = min(class_distribution, key=class_distribution.get)
    return next(cls for cls in available_classes if cls.id == recommended_class)


def recommend_hostel_allocation(applicant, available_hostels):
    """
    Recommends hostel based on gender and space availability.
    """
    matching_hostels = [h for h in available_hostels if h.gender in [applicant.gender, 'any'] and h.capacity > h.occupants.count()]
    if not matching_hostels:
        return None
    return sorted(matching_hostels, key=lambda h: h.occupants.count())[0]


def generate_offer_letter(applicant):
    """
    Auto-generate offer letter PDF using HTML template.
    """
    context = {
        "applicant": applicant,
        "date": timezone.now().date(),
        "institution": applicant.admission_session.institution,
        "expiry_date": timezone.now().date() + timedelta(days=14),
    }
    html_string = render_to_string("admissions/offer_letter_template.html", context)
    pdf_file = HTML(string=html_string).write_pdf()

    return ContentFile(pdf_file, name=f"Offer_Letter_{applicant.id}.pdf")


def highlight_special_applicants():
    """
    Returns applicants that may need special attention:
    - Very high entrance score
    - Talent flagged
    - Orphaned or chronic illness
    """
    special_cases = Applicant.objects.filter(
        entranceexam__score__gte=85
    ) | Applicant.objects.filter(
        talents__isnull=False
    ) | Applicant.objects.filter(
        orphan_status__in=['partial', 'full']
    ) | Applicant.objects.filter(
        has_chronic_illness=True
    )
    return special_cases.distinct()


def generate_admission_summary_for_review():
    """
    Generates a short summary of applicant stats for admin/board meeting.
    """
    total = Applicant.objects.count()
    shortlisted = Applicant.objects.filter(application_status='shortlisted').count()
    accepted = Applicant.objects.filter(application_status='accepted').count()
    enrolled = Applicant.objects.filter(application_status='enrolled').count()
    chronic = Applicant.objects.filter(has_chronic_illness=True).count()
    special = highlight_special_applicants().count()

    return {
        "total_applicants": total,
        "shortlisted": shortlisted,
        "accepted": accepted,
        "enrolled": enrolled,
        "special_cases": special,
        "with_chronic_illness": chronic,
    }
