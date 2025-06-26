from celery import shared_task
from django.db import models
from django.utils import timezone
from .models import AcademicYear, Term, AcademicEvent, AcademicAuditLog
from accounts.models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import timedelta


@shared_task
def deactivate_old_academic_years():
    """Automatically deactivate academic years that have ended"""
    today = timezone.now().date()
    expired_years = AcademicYear.objects.filter(end_date__lt=today, is_current=True)
    for year in expired_years:
        year.is_current = False
        year.save()
        AcademicAuditLog.objects.create(
            actor=None,
            action='update',
            model_name='AcademicYear',
            record_id=year.id,
            notes='Automatically marked as inactive by task.'
        )


@shared_task
def notify_term_start():
    """Notify institution users on the start day of a new term"""
    today = timezone.now().date()
    starting_terms = Term.objects.filter(start_date=today)
    for term in starting_terms:
        users = CustomUser.objects.filter(institution=term.academic_year.institution)
        for user in users:
            if user.email:
                context = {
                    'user': user,
                    'term': term,
                    'year': term.academic_year,
                }
                message = render_to_string('emails/term_start.txt', context)
                send_mail(
                    subject=f"{term.name} Starts Today - {term.academic_year.name}",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )


@shared_task
def generate_term_reminder():
    """Send midterm and end-of-term reminders to staff"""
    today = timezone.now().date()
    reminders = Term.objects.filter(
        models.Q(midterm_date=today) | models.Q(end_date=today)
    )
    for term in reminders:
        subject = f"Reminder: {'Midterm' if term.midterm_date == today else 'End of Term'} - {term.name}"
        users = CustomUser.objects.filter(institution=term.academic_year.institution)
        for user in users:
            if user.email:
                message = (
                    f"Hello {user.first_name},\n\n"
                    f"This is a reminder that today marks the {'midterm' if term.midterm_date == today else 'end'} of {term.name}.\n"
                    f"Academic Year: {term.academic_year.name}.\n\nRegards,\nEduOS System"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


@shared_task
def summarize_academic_events():
    """Send a weekly summary of upcoming academic events"""
    upcoming = timezone.now().date() + timedelta(days=7)
    events = AcademicEvent.objects.filter(start_date__lte=upcoming, start_date__gte=timezone.now().date())
    institutions = set(event.institution for event in events)

    for institution in institutions:
        institution_users = CustomUser.objects.filter(institution=institution)
        user_emails = [u.email for u in institution_users if u.email]
        institution_events = events.filter(institution=institution)

        context = {'events': institution_events, 'institution': institution}
        message = render_to_string('emails/event_summary.txt', context)
        send_mail(
            subject=f"Upcoming Academic Events - {institution.name}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=user_emails,
            fail_silently=True,
        )
