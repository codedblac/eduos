from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.conf import settings
from institutions.models import Institution
from students.models import Student
from teachers.models import Teacher
from accounts.models import CustomUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = settings.AUTH_USER_MODEL

class IDCardTemplate(models.Model):
    """
    Admin-defined ID card template per institution.
    Controls layout, fields, colors, logo, and design elements.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    background_color = models.CharField(max_length=20, default="#FFFFFF")
    text_color = models.CharField(max_length=20, default="#000000")
    font = models.CharField(max_length=100, default="Arial")
    include_qr_code = models.BooleanField(default=True)
    include_barcode = models.BooleanField(default=False)
    include_signature = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='id_cards/templates/logos/', null=True, blank=True)
    background_image = models.ImageField(upload_to='id_cards/templates/backgrounds/', null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.institution.name}"


class IDCard(models.Model):
    """
    Represents a single ID card issued to any user type.
    Uses GenericForeignKey to support different user models.
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('staff', 'Staff'),
        ('admin', 'Administrator'),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(IDCardTemplate, on_delete=models.SET_NULL, null=True)
    
    # Generic reference (e.g. Student, Teacher, Staff)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    profile_object = GenericForeignKey('content_type', 'object_id')

    unique_id = models.CharField(max_length=100, unique=True)  # Student ID / Teacher ID / Staff ID
    full_name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='id_cards/photos/')
    qr_code_image = models.ImageField(upload_to='id_cards/qr/', null=True, blank=True)
    barcode_image = models.ImageField(upload_to='id_cards/barcodes/', null=True, blank=True)
    class_or_department = models.CharField(max_length=100, blank=True)
    issued_on = models.DateField(default=timezone.now)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    revoked = models.BooleanField(default=False)
    reason_revoked = models.TextField(blank=True)

    digital_only = models.BooleanField(default=False)
    printed = models.BooleanField(default=False)
    last_printed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ID: {self.full_name} ({self.role})"


class IDCardAuditLog(models.Model):
    """
    Logs creation, update, print, revoke, and reissue actions on IDs.
    """
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('printed', 'Printed'),
        ('revoked', 'Revoked'),
        ('reissued', 'Reissued'),
        ('auto-regenerated', 'Auto-Regenerated'),
    ]

    id_card = models.ForeignKey(IDCard, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} on {self.id_card} by {self.performed_by}"


class IDCardReissueRequest(models.Model):
    """
    If a user requests a new ID (lost/damaged/updated info).
    Staff can approve and trigger re-issuance.
    """
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    handled_by = models.ForeignKey(User, related_name='id_reissue_handler', on_delete=models.SET_NULL, null=True, blank=True)
    approved_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reissue Request by {self.requester}"


class DigitalIDToken(models.Model):
    """
    Token to verify identity digitally via QR scan or mobile app.
    """
    id_card = models.OneToOneField(IDCard, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Digital token for {self.id_card}"
