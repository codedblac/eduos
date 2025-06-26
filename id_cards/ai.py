# id_cards/ai.py

import qrcode
import io
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from .models import IDCard
from django.utils import timezone


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
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        filename = f"qr_{timezone.now().timestamp()}.png"
        return ContentFile(buffer.getvalue(), name=filename)

    def auto_generate_id_card(self, user_profile):
        """
        Generate an ID card for a user (student, teacher, staff).
        Only runs if no active ID exists.
        """
        if IDCard.objects.filter(user=user_profile.user, is_active=True).exists():
            return None  # Already exists

        qr_data = f"{settings.SITE_URL}/verify/id/{user_profile.user.id}/"
        qr_image = self.generate_qr_code(qr_data)

        id_card = IDCard.objects.create(
            user=user_profile.user,
            institution=self.institution,
            role=user_profile.get_role_display(),
            qr_code=qr_image,
            photo=user_profile.photo if hasattr(user_profile, 'photo') else None,
            name=user_profile.full_name if hasattr(user_profile, 'full_name') else user_profile.user.get_full_name(),
            id_number=user_profile.user_id if hasattr(user_profile, 'user_id') else user_profile.user.id,
            department=user_profile.department.name if hasattr(user_profile, 'department') else '',
            class_level=user_profile.class_level.name if hasattr(user_profile, 'class_level') else '',
            valid_until=timezone.now().date().replace(year=timezone.now().year + 1)
        )
        return id_card

    def bulk_generate_missing_ids(self):
        """
        Auto-generate missing ID cards for all active users in the institution.
        Returns a count of how many were created.
        """
        from students.models import Student
        from teachers.models import Teacher
        from accounts.models import CustomUser

        created = 0

        # Process students
        for student in Student.objects.filter(institution=self.institution, is_active=True):
            if not IDCard.objects.filter(user=student.user, is_active=True).exists():
                if self.auto_generate_id_card(student):
                    created += 1

        # Process teachers
        for teacher in Teacher.objects.filter(institution=self.institution, is_active=True):
            if not IDCard.objects.filter(user=teacher.user, is_active=True).exists():
                if self.auto_generate_id_card(teacher):
                    created += 1

        # Optionally process staff/admins
        for user in CustomUser.objects.filter(institution=self.institution, is_active=True, is_staff=True):
            if not IDCard.objects.filter(user=user, is_active=True).exists():
                if self.auto_generate_id_card(user):
                    created += 1

        return created

    def regenerate_on_update(self, user_profile):
        """
        Triggered when key fields (e.g., photo, name, class) change.
        Deactivates old card, creates new one.
        """
        IDCard.objects.filter(user=user_profile.user, is_active=True).update(is_active=False)

        return self.auto_generate_id_card(user_profile)
