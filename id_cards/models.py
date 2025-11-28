import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from institutions.models import Institution

User = settings.AUTH_USER_MODEL


class IDCardTemplate(models.Model):
    """
    Institution-specific design template for ID cards.
    Controls layout, branding, fonts, colors, and QR/barcode.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="id_card_templates")
    name = models.CharField(max_length=100)
    background_color = models.CharField(max_length=20, default="#FFFFFF")
    text_color = models.CharField(max_length=20, default="#000000")
    font = models.CharField(max_length=100, default="Arial")
    logo = models.ImageField(upload_to='id_cards/templates/logos/', null=True, blank=True)
    background_image = models.ImageField(upload_to='id_cards/templates/backgrounds/', null=True, blank=True)

    include_qr_code = models.BooleanField(default=True)
    include_barcode = models.BooleanField(default=False)
    include_signature = models.BooleanField(default=False)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('institution', 'name')

    def __str__(self):
        return f"{self.name} - {self.institution.name}"


class IDCard(models.Model):
    """
    ERP-ready ID Card Model for multiple roles and flexible user assignment.
    Uses GenericForeignKey for polymorphic identity assignment (Student, Teacher, Staff, etc.).
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('staff', 'Staff'),
        ('admin', 'Administrator'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="id_cards")
    primary_role= models.CharField(max_length=20, choices=ROLE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="id_cards")
    template = models.ForeignKey(IDCardTemplate, on_delete=models.SET_NULL, null=True, related_name="id_cards")

    # Generic user profile (Student, Teacher, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    profile_object = GenericForeignKey('content_type', 'object_id')

    unique_id = models.CharField(max_length=100, unique=True)  # e.g. Admission Number, Staff ID
    full_name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='id_cards/photos/')
    qr_code_image = models.ImageField(upload_to='id_cards/qr/', null=True, blank=True)
    barcode_image = models.ImageField(upload_to='id_cards/barcodes/', null=True, blank=True)
    class_or_department = models.CharField(max_length=100, blank=True)

    issued_on = models.DateField(default=timezone.now)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    reason_revoked = models.TextField(blank=True)

    digital_only = models.BooleanField(default=False)
    printed = models.BooleanField(default=False)
    last_printed_on = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.primary_role}) - {self.unique_id}"


class IDCardAuditLog(models.Model):
    """
    Track actions like create, print, revoke, or auto-regeneration of ID cards.
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
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="performed_id_actions")
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} - {self.id_card.full_name} @ {self.timestamp}"


class IDCardReissueRequest(models.Model):
    """
    Request to reissue ID due to loss, damage, update, etc.
    """
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='id_card_reissue_requests')
    reason = models.TextField()
    approved = models.BooleanField(default=False)
    handled_by = models.ForeignKey(User, related_name='id_card_reissue_approvals', on_delete=models.SET_NULL, null=True, blank=True)
    approved_on = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reissue Request: {self.requester}"


class DigitalIDToken(models.Model):
    """
    Digital identity token for app or QR code verification.
    Can be used for biometric/NFC integrations later.
    """
    id_card = models.OneToOneField(IDCard, on_delete=models.CASCADE, related_name='digital_token')
    token = models.CharField(max_length=128, unique=True)
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Digital Token for {self.id_card.full_name}"
