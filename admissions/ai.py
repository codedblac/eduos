import random
from datetime import timedelta
from django.utils import timezone
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Applicant, EntranceExam, AdmissionOffer, AdmissionSession


def suggest_admission_offer(applicant):
    """
    Rule-based admission decision helper.
    - Requires applicant to pass entrance exam with >= 50%.
    - Can be swapped with ML logic.
    """
    exam = EntranceExam.objects.filter(applicant=applicant).first()
    if exam and exam.passed and exam.score and exam.score >= 50:
        return True
    return False


def predict_success_probability(applicant):
    """
    Estimate applicant's future performance likelihood.
    Can be improved by ML based on academic records & demographics.
    """
    base_score = 0.5  # baseline

    # Adjust based on entrance score
    exam = EntranceExam.objects.filter(applicant=applicant).first()
    if exam and exam.score is not None:
        base_score += (float(exam.score) - 50) / 100

    # Penalize support-needing applicants slightly
    if applicant.has_disability:
        base_score -= 0.05
    if applicant.has_chronic_illness:
        base_score -= 0.05

    # Boost for talents or leadership interest
    if applicant.talents:
        base_score += 0.05

    return round(min(max(base_score, 0), 1), 2)  # Clamp between 0-1


def rank_applicants_by_potential(applicants):
    """
    Rank applicants using predictive scoring logic.
    """
    return sorted(applicants, key=lambda a: predict_success_probability(a), reverse=True)


def recommend_class_allocation(applicant, available_classes):
    """
    Recommend least-loaded class for applicant.
    Requires .student_set on each class (prefetch recommended).
    """
    class_distribution = {
        cls.id: cls.student_set.count() for cls in available_classes
    }
    min_loaded_id = min(class_distribution, key=class_distribution.get)
    return next(cls for cls in available_classes if cls.id == min_loaded_id)


def recommend_hostel_allocation(applicant, available_hostels):
    """
    Recommend hostel by gender and space.
    Hostel must have `.occupants.count()` and `.gender` field.
    """
    matching_hostels = [
        hostel for hostel in available_hostels
        if hostel.gender in [applicant.gender, 'any'] and hostel.occupants.count() < hostel.capacity
    ]
    if not matching_hostels:
        return None
    return sorted(matching_hostels, key=lambda h: h.occupants.count())[0]


def generate_offer_letter(applicant):
    """
    Auto-generate PDF admission letter using WeasyPrint and template.
    """
    context = {
        "applicant": applicant,
        "institution": applicant.admission_session.institution,
        "date": timezone.now().date(),
        "expiry_date": timezone.now().date() + timedelta(days=14),
    }

    html_string = render_to_string("admissions/offer_letter_template.html", context)
    pdf_file = HTML(string=html_string).write_pdf()
    return ContentFile(pdf_file, name=f"Offer_Letter_{applicant.id}.pdf")


def highlight_special_applicants():
    """
    Return queryset of applicants flagged for:
    - High score
    - Orphaned
    - Chronic illness
    - Talented
    """
    return Applicant.objects.filter(
        entranceexam__score__gte=85
    ).union(
        Applicant.objects.filter(orphan_status__in=['partial', 'full']),
        Applicant.objects.filter(has_chronic_illness=True),
        Applicant.objects.exclude(talents__isnull=True).exclude(talents__exact='')
    ).distinct()


def generate_admission_summary_for_review():
    """
    Return high-level applicant stats for review dashboards or PDFs.
    """
    total = Applicant.objects.count()
    shortlisted = Applicant.objects.filter(application_status='shortlisted').count()
    accepted = Applicant.objects.filter(application_status='accepted').count()
    enrolled = Applicant.objects.filter(application_status='enrolled').count()
    chronic = Applicant.objects.filter(has_chronic_illness=True).count()
    orphaned = Applicant.objects.filter(orphan_status__in=['partial', 'full']).count()
    special = highlight_special_applicants().count()

    return {
        "total_applicants": total,
        "shortlisted": shortlisted,
        "accepted": accepted,
        "enrolled": enrolled,
        "special_cases": special,
        "with_chronic_illness": chronic,
        "orphans": orphaned,
    }

def recommend_admission_status(application):
    if application.average_score >= 85 and application.age <= 20:
        return "Accepted"
    elif application.average_score >= 70:
        return "Waitlisted"
    else:
        return "Rejected"