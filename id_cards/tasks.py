# id_cards/tasks.py

import uuid
from io import BytesIO
from celery import shared_task
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

from weasyprint import HTML

from .models import IDCard, IDCardTemplate
from students.models import Student
from teachers.models import Teacher
from accounts.models import CustomUser


@shared_task
def generate_id_card(user_id, role):
    """
    Generate an ID card for a single user based on their role.
    """
    try:
        # Get the user object
        if primary_role== 'student':
            user = Student.objects.get(id=user_id)
        elif primary_role== 'teacher':
            user = Teacher.objects.get(id=user_id)
        else:
            user = CustomUser.objects.get(id=user_id)

        institution = getattr(user, 'institution', None)
        if not institution and hasattr(user, 'profile'):
            institution = getattr(user.profile, 'institution', None)

        if not institution:
            return f"Institution not found for user {user_id}"

        template = IDCardTemplate.objects.filter(institution=institution).first()
        if not template:
            return f"No ID card template found for institution: {institution.name}"

        # Prepare context and render PDF
        valid_until = now().date().replace(year=now().year + 1)
        context = {
            'user': user,
            'template': template,
            'date_issued': now().date(),
            'valid_until': valid_until,
        }

        html_string = render_to_string('id_cards/id_card_template.html', context)
        html = HTML(string=html_string)
        pdf_file = BytesIO()
        html.write_pdf(target=pdf_file)

        # Create and attach the ID card
        id_card = IDCard.objects.create(
            user=user.user if hasattr(user, 'user') else user,
            institution=institution,
            primary_role=role,
            template=template,
            issued_on=now(),
            expiry_date=valid_until
        )
        id_card.file.save(f"idcard_{uuid.uuid4().hex}.pdf", ContentFile(pdf_file.getvalue()))
        id_card.save()

        return f"ID card generated for {user}"
    except Exception as e:
        return f"Error generating ID card for user {user_id}: {str(e)}"


@shared_task
def bulk_generate_id_cards(user_ids, role):
    """
    Bulk generate ID cards for a list of users based on role.
    """
    results = []
    for user_id in user_ids:
        result = generate_id_card(user_id, role)
        results.append(result)
    return results


@shared_task
def regenerate_id_cards_on_profile_update(user_id):
    """
    Regenerate an ID card if user profile is updated (e.g. photo or name).
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        existing_card = IDCard.objects.filter(user=user).first()
        if existing_card:
            existing_card.delete()
        return generate_id_card(user.id, user.primary_role)
    except Exception as e:
        return f"Error regenerating ID card for user {user_id}: {str(e)}"
