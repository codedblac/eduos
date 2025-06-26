# admissions/tasks.py

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import AdmissionOffer, Applicant, EntranceExam
from students.models import Student
from accounts.models import CustomUser


@shared_task
def expire_old_offers():
    """
    Mark offers as expired if past expiry_date and still pending.
    """
    today = timezone.now().date()
    offers = AdmissionOffer.objects.filter(status='pending', expiry_date__lt=today)
    for offer in offers:
        offer.status = 'expired'
        offer.save(update_fields=['status'])


@shared_task
def notify_shortlisted_applicant(applicant_id):
    """
    Notify applicant (email/SMS) if shortlisted.
    """
    try:
        applicant = Applicant.objects.get(id=applicant_id)
        if applicant.email:
            send_mail(
                subject="You have been shortlisted!",
                message=f"Dear {applicant.first_name},\n\nYou have been shortlisted for admission.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[applicant.email]
            )
        # Future: SMS logic here (Africa's Talking, Twilio, etc.)
    except Applicant.DoesNotExist:
        pass


@shared_task
def enroll_applicant_to_student(applicant_id):
    """
    Convert an accepted applicant to a Student.
    """
    try:
        applicant = Applicant.objects.get(id=applicant_id)

        student = Student.objects.create(
            first_name=applicant.first_name,
            last_name=applicant.last_name,
            other_names=applicant.other_names,
            gender=applicant.gender,
            date_of_birth=applicant.date_of_birth,
            class_level=applicant.entry_class_level,
            admission_number=f"{applicant.admission_session.name}-{applicant.id}",
            institution=applicant.admission_session.institution,
            email=applicant.email,
            phone=applicant.phone,
            photo=applicant.passport_photo,
            career_dream=applicant.career_dream,
            talents=applicant.talents,
            allergies=applicant.allergies,
        )

        applicant.application_status = 'enrolled'
        applicant.save(update_fields=['application_status'])

        return student.id
    except Applicant.DoesNotExist:
        return None


@shared_task
def send_bulk_offer_notifications():
    """
    Notify all pending applicants with valid offers.
    """
    offers = AdmissionOffer.objects.filter(status='pending')
    for offer in offers:
        applicant = offer.applicant
        if applicant.email:
            send_mail(
                subject="Your Admission Offer",
                message=f"Dear {applicant.first_name},\n\nPlease check your admission offer attached.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[applicant.email]
            )
