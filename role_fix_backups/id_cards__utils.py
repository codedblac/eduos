import os
import io
import qrcode
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.pagesizes import IDCard
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from django.core.files.storage import default_storage
from .models import IDCardTemplate


def generate_qr_code(data: str, box_size=10, border=4) -> Image.Image:
    """
    Generate a QR code image for the given data.
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=box_size,
        border=border
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def resize_image(image: Image.Image, size=(300, 300)) -> Image.Image:
    """
    Resize an image (e.g., passport photo) to fit the ID card dimensions.
    """
    return image.resize(size, Image.LANCZOS)


def get_id_file_path(instance, filename: str) -> str:
    """
    Get the upload path for storing ID card files.
    """
    ext = filename.split('.')[-1]
    filename = f"{instance.user.username}_id_card.{ext}"
    return os.path.join('id_cards/generated/', filename)


def generate_id_card_pdf(id_card: IDCardTemplate) -> ContentFile:
    """
    Generate a print-ready PDF for the ID card.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=IDCard)

    user = id_card.user
    profile = getattr(user, 'student_profile', None) or getattr(user, 'teacher_profile', None)

    # Layout
    c.setFont("Helvetica-Bold", 10)
    c.drawString(10 * mm, 45 * mm, f"Name: {user.get_full_name()}")
    c.drawString(10 * mm, 40 * mm, f"Role: {id_card.primary_role}")
    c.drawString(10 * mm, 35 * mm, f"ID No: {user.username}")

    if profile:
        class_or_dept = getattr(profile, 'class_level', None) or getattr(profile, 'department', None)
        if class_or_dept:
            c.drawString(10 * mm, 30 * mm, f"Class/Dept: {class_or_dept.name}")

    if id_card.institution:
        c.setFont("Helvetica", 8)
        c.drawString(10 * mm, 20 * mm, f"Institution: {id_card.institution.name}")
        if id_card.institution.phone_number:
            c.drawString(10 * mm, 15 * mm, f"Contact: {id_card.institution.phone_number}")

    # Add QR Code
    qr_img = generate_qr_code(data=str(user.username))
    qr_io = io.BytesIO()
    qr_img.save(qr_io, format='PNG')
    qr_io.seek(0)
    c.drawInlineImage(qr_io, 60 * mm, 5 * mm, width=25 * mm, height=25 * mm)

    c.showPage()
    c.save()
    buffer.seek(0)

    return ContentFile(buffer.read(), name=f"{user.username}_id_card.pdf")


def save_pdf_to_id_card(id_card: IDCardTemplate):
    """
    Generate and attach a PDF file to an IDCardTemplate model instance.
    """
    content = generate_id_card_pdf(id_card)
    file_path = get_id_file_path(id_card, content.name)
    saved_path = default_storage.save(file_path, content)
    id_card.pdf_file.name = saved_path
    id_card.save(update_fields = ["pdf_file"])


def validate_id_card_data(user) -> tuple[bool, str]:
    """
    Check if user has all the necessary profile data to generate an ID card.
    """
    required_fields = ['first_name', 'last_name', 'username']
    missing = [f for f in required_fields if not getattr(user, f, None)]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    return True, "Valid"
