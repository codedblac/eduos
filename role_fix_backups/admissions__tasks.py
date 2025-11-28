from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import AdmissionOffer, Applicant
from students.models import Student
import logging

logger = logging.getLogger(__name__)


@shared_task
def expire_old_offers():
    """
    Automatically mark all pending admission offers as expired if past expiry date.
    """
    today = timezone.now().date()
    expired_offers = AdmissionOffer.objects.filter(status='pending', expiry_date__lt=today)
    count = expired_offers.update(status='expired')
    logger.info(f"[Admissions] Expired {count} outdated admission offers.")


@shared_task
def notify_shortlisted_applicant(applicant_id):
    """
    Send an email notification to a shortlisted applicant.
    Future support: SMS via Africa's Talking, Twilio, etc.
    """
    try:
        applicant = Applicant.objects.get(id=applicant_id)
        if applicant.email:
            subject = "🎉 You've been shortlisted for admission!"
            message = render_to_string("emails/applicant_shortlisted.txt", {"applicant": applicant})
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [applicant.email])
            logger.info(f"[Admissions] Shortlist notification sent to {applicant.email}")
    except Applicant.DoesNotExist:
        logger.warning(f"[Admissions] Applicant ID {applicant_id} does not exist.")


@shared_task
def enroll_applicant_to_student(applicant_id):
    """
    Converts an accepted applicant into a registered student.
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
            admission_number=f"{applicant.admission_session.name.replace(' ', '')}-{applicant.id}",
            institution=applicant.admission_session.institution,
            email=applicant.email,
            phone=applicant.phone,
            photo=applicant.passport_photo,
            career_dream=applicant.career_dream,
            talents=applicant.talents,
            allergies=applicant.allergies,
        )

        applicant.application_status = 'enrolled'
        applicant.save(update_fields = ['application_status'])

        logger.info(f"[Admissions] Enrolled applicant {applicant.id} as student {student.id}")
        return student.id

    except Applicant.DoesNotExist:
        logger.error(f"[Admissions] Applicant ID {applicant_id} does not exist.")
        return None


@shared_task
def send_bulk_offer_notifications():
    """
    Sends offer notifications to all applicants with pending, non-expired offers.
    """
    today = timezone.now().date()
    offers = AdmissionOffer.objects.filter(status='pending', expiry_date__gte=today)

    success_count = 0
    for offer in offers:
        applicant = offer.applicant
        if applicant.email:
            try:
                message = render_to_string("emails/admission_offer.txt", {
                    "applicant": applicant,
                    "offer": offer,
                })
                send_mail(
                    subject="📩 Your Admission Offer from EduOS School",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[applicant.email],
                )
                success_count += 1
            except Exception as e:
                logger.error(f"[Admissions] Error sending offer to {applicant.email}: {e}")

    logger.info(f"[Admissions] Sent {success_count} admission offer notifications.")
