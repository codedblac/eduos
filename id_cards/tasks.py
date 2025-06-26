# id_cards/tasks.py

from celery import shared_task
from django.core.files.base import ContentFile
from django.utils.timezone import now
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
from .models import IDCard, IDCardTemplate
from students.models import Student
from accounts.models import CustomUser
from teachers.models import Teacher
from django.conf import settings
import os
import uuid

@shared_task
def generate_id_card(user_id, role):
    """
    Generates an ID card for a single user (Student, Teacher, Admin, or Staff)
    """
    try:
        if role == 'student':
            user = Student.objects.get(id=user_id)
        elif role == 'teacher':
            user = Teacher.objects.get(id=user_id)
        else:
            user = CustomUser.objects.get(id=user_id)

        institution = user.institution if hasattr(user, 'institution') else user.profile.institution
        template = IDCardTemplate.objects.filter(institution=institution).first()
        if not template:
            return f"No template found for institution {institution.name}"

        context = {
            'user': user,
            'template': template,
            'date_issued': now().date(),
            'valid_until': now().date().replace(year=now().year + 1),
        }

        html_string = render_to_string('id_cards/id_card_template.html', context)
        html = HTML(string=html_string)
        pdf_file = BytesIO()
        html.write_pdf(target=pdf_file)

        card = IDCard.objects.create(
            user=user if isinstance(user, CustomUser) else user.user,
            institution=institution,
            role=role,
            template=template,
            issued_on=now(),
            valid_until=context['valid_until']
        )
        card.file.save(f"idcard_{uuid.uuid4().hex}.pdf", ContentFile(pdf_file.getvalue()))
        card.save()
        return f"ID Card generated for {user}"
    except Exception as e:
        return str(e)


@shared_task
def bulk_generate_id_cards(user_ids, role):
    """
    Bulk generates ID cards for a list of user IDs.
    """
    results = []
    for uid in user_ids:
        result = generate_id_card(uid, role)
        results.append(result)
    return results


@shared_task
def regenerate_id_cards_on_profile_update(user_id):
    """
    Regenerates ID card for a user if their profile (photo, name, role, etc.) changes.
    """
    user = CustomUser.objects.get(id=user_id)
    card = IDCard.objects.filter(user=user).first()
    if card:
        card.delete()
    return generate_id_card(user_id=user.id, role=user.role)

