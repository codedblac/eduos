from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import CommunicationAnnouncement, CommunicationLog, CommunicationTarget
from accounts.models import CustomUser


@shared_task
def send_announcement_now(announcement_id):
    try:
        announcement = CommunicationAnnouncement.objects.get(id=announcement_id)
        if announcement.sent:
            return "Already sent."

        # Collect recipients
        recipients = get_announcement_recipients(announcement)
        emails = []

        for user in recipients:
            context = {
                'user': user,
                'announcement': announcement,
                'institution': announcement.institution,
            }
            subject = f"[{announcement.priority.upper()}] {announcement.title}"
            message = render_to_string("communications/email/announcement_email.txt", context)
            html_message = render_to_string("communications/email/announcement_email.html", context)
            emails.append((subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]))

        # Send all
        send_mass_mail(emails, fail_silently=False)

        # Mark as sent
        announcement.sent = True
        announcement.save()

        # Log
        CommunicationLog.objects.create(
            announcement=announcement,
            status="sent",
            details=f"Sent to {len(recipients)} users"
        )
        return f"Announcement sent to {len(recipients)} recipients."

    except CommunicationAnnouncement.DoesNotExist:
        return "Announcement not found."
    except Exception as e:
        CommunicationLog.objects.create(
            announcement_id=announcement_id,
            status="error",
            details=str(e)
        )
        return f"Error: {str(e)}"


@shared_task
def send_scheduled_announcements():
    """
    Runs periodically (every minute or 5 min) via Celery beat.
    """
    now = timezone.now()
    scheduled = CommunicationAnnouncement.objects.filter(
        scheduled_at__lte=now,
        sent=False
    )
    for announcement in scheduled:
        send_announcement_now.delay(announcement.id)


def get_announcement_recipients(announcement):
    """
    Collects users targeted by the announcement.
    """
    targets = CommunicationTarget.objects.filter(announcement=announcement)
    users = set()

    for target in targets:
        if target.user:
            users.add(target.user)
        elif target.role:
            users.update(CustomUser.objects.filter(role=target.role))
        elif target.class_level or target.stream:
            qs = CustomUser.objects.filter(role="student")
            if target.class_level:
                qs = qs.filter(student_profile__class_level=target.class_level)
            if target.stream:
                qs = qs.filter(student_profile__stream=target.stream)
            users.update(qs)

    return list(users)
