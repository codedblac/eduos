# id_cards/ai.py

import io
import qrcode
import logging
from PIL import Image
from typing import Optional
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile

from .models import IDCard

logger = logging.getLogger(__name__)


class IDCardAIEngine:
    """
    AI-powered utilities for smart ID card generation, regeneration,
    and personalization within EduOS.
    """

    def __init__(self, institution):
        self.institution = institution

    def generate_qr_code(self, data: str) -> ContentFile:
        """
        Generate a QR code image from the given data (e.g., user ID, verification URL).
        Returns a Django File object suitable for saving in a model field.
        """
        logger.debug(f"Generating QR code for data: {data}")
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        filename = f"qr_{timezone.now().timestamp()}.png"

        logger.info(f"QR code generated: {filename}")
        return ContentFile(buffer.getvalue(), name=filename)

    def auto_generate_id_card(self, user_profile) -> Optional[IDCard]:
        """
        Generate an ID card for a user (student, teacher, staff) if none is active.
        """
        user = getattr(user_profile, 'user', user_profile)
        if IDCard.objects.filter(user=user, is_active=True).exists():
            logger.info(f"Active ID card already exists for user {user}")
            return None

        qr_data = f"{settings.SITE_URL}/verify/id/{user.id}/"
        qr_image = self.generate_qr_code(qr_data)

        id_card = IDCard.objects.create(
            user=user,
            institution=self.institution,
            primary_role=getattr(user_profile, 'get_role_display', lambda: 'UNKNOWN')(),
            qr_code=qr_image,
            photo=getattr(user_profile, 'photo', None),
            name=getattr(user_profile, 'full_name', user.get_full_name()),
            id_number=getattr(user_profile, 'user_id', user.id),
            department=getattr(getattr(user_profile, 'department', None), 'name', ''),
            class_level=getattr(getattr(user_profile, 'class_level', None), 'name', ''),
            valid_until=timezone.now().date().replace(year=timezone.now().year + 1)
        )

        logger.info(f"ID card created for user {user.id}: {id_card.id}")
        return id_card

    def bulk_generate_missing_ids(self) -> int:
        """
        Auto-generate missing ID cards for all eligible active users in the institution.
        Returns the number of ID cards created.
        """
        from students.models import Student
        from teachers.models import Teacher
        from accounts.models import CustomUser

        created_count = 0

        # Students
        students = Student.objects.filter(institution=self.institution, is_active=True)
        for student in students:
            if not IDCard.objects.filter(user=student.user, is_active=True).exists():
                if self.auto_generate_id_card(student):
                    created_count += 1

        # Teachers
        teachers = Teacher.objects.filter(institution=self.institution, is_active=True)
        for teacher in teachers:
            if not IDCard.objects.filter(user=teacher.user, is_active=True).exists():
                if self.auto_generate_id_card(teacher):
                    created_count += 1

        # Staff/Admins
        staff_users = CustomUser.objects.filter(
            institution=self.institution,
            is_active=True,
            is_staff=True
        )
        for staff in staff_users:
            if not IDCard.objects.filter(user=staff, is_active=True).exists():
                if self.auto_generate_id_card(staff):
                    created_count += 1

        logger.info(f"Total new ID cards generated: {created_count}")
        return created_count

    def regenerate_on_update(self, user_profile) -> Optional[IDCard]:
        """
        Regenerates an ID card when critical profile info is updated.
        Deactivates old card and creates a new one.
        """
        user = getattr(user_profile, 'user', user_profile)

        existing_cards = IDCard.objects.filter(user=user, is_active=True)
        if existing_cards.exists():
            existing_cards.update(is_active=False)
            logger.info(f"Deactivated existing ID cards for user {user.id}")

        return self.auto_generate_id_card(user_profile)
