from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import timedelta

from .models import AcademicYear, Term, AcademicEvent, AcademicAuditLog
from accounts.models import CustomUser


@shared_task
def deactivate_old_academic_years():
    """
    Automatically deactivate academic years that have ended.
    Logs the action in AcademicAuditLog.
    """
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
            notes='Automatically marked as inactive after end date by scheduled task.'
        )


@shared_task
def notify_term_start():
    """
    Send email notifications to users of an institution when a new term starts today.
    """
    today = timezone.now().date()
    starting_terms = Term.objects.filter(start_date=today)
    
    for term in starting_terms:
        users = CustomUser.objects.filter(institution=term.academic_year.institution, email__isnull=False)
        
        for user in users:
            context = {
                'user': user,
                'term': term,
                'year': term.academic_year,
            }
            message = render_to_string('emails/term_start.txt', context)
            
            send_mail(
                subject=f"{term.name} Begins Today - {term.academic_year.name}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )


@shared_task
def generate_term_reminder():
    """
    Send reminders to users on midterm and end-of-term dates.
    """
    today = timezone.now().date()
    terms = Term.objects.filter(Q(midterm_date=today) | Q(end_date=today))
    
    for term in terms:
        event_type = "Midterm" if term.midterm_date == today else "End of Term"
        subject = f"Reminder: {event_type} - {term.name}"
        
        users = CustomUser.objects.filter(institution=term.academic_year.institution, email__isnull=False)
        
        for user in users:
            message = (
                f"Dear {user.first_name},\n\n"
                f"This is a reminder that today is the {event_type.lower()} for {term.name}.\n"
                f"Academic Year: {term.academic_year.name}.\n\n"
                f"Regards,\nEduOS System"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )


@shared_task
def summarize_academic_events():
    """
    Weekly summary email of upcoming academic events per institution.
    """
    today = timezone.now().date()
    upcoming = today + timedelta(days=7)
    
    events = AcademicEvent.objects.filter(start_date__gte=today, start_date__lte=upcoming)
    institutions = set(events.values_list('institution', flat=True))
    
    for institution_id in institutions:
        institution_events = events.filter(institution_id=institution_id)
        users = CustomUser.objects.filter(institution_id=institution_id, email__isnull=False)
        emails = [u.email for u in users]

        if not emails:
            continue

        context = {
            'events': institution_events,
            'institution': institution_events.first().institution if institution_events.exists() else None
        }
        message = render_to_string('emails/event_summary.txt', context)
        
        send_mail(
            subject=f"Upcoming Academic Events - {context['institution'].name}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True,
        )
