from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


# =========================
# Institution / School Types
# =========================
class InstitutionType(models.TextChoices):
    PRIMARY = "PRIMARY", _("Primary School")
    SECONDARY = "SECONDARY", _("Secondary School")
    UNIVERSITY = "UNIVERSITY", _("University")
    TECHNICAL = "TECHNICAL", _("Technical Institute")
    VIRTUAL = "VIRTUAL", _("Virtual School")
    OTHER = "OTHER", _("Other")


class SchoolType(models.TextChoices):
    PUBLIC = 'public', _('Public')
    PRIVATE = 'private', _('Private')
    COMMUNITY = 'community', _('Community')
    OTHER = 'other', _('Other')


# =========================
# Institution Model
# =========================
class Institution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic info
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)

    # Location & contact
    country = models.CharField(max_length=100, db_index=True)
    county = models.CharField(max_length=100, db_index=True)
    sub_county = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    ward = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    village = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Branding / theming
    logo = models.ImageField(upload_to='institution_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=20, default="#0047AB")
    secondary_color = models.CharField(max_length=20, default="#FFFFFF")
    theme_mode = models.CharField(max_length=10, choices=[('light', _('Light')), ('dark', _('Dark'))], default='light')

    # Classification
    school_type = models.CharField(max_length=20, choices=SchoolType.choices, default=SchoolType.OTHER)
    institution_type = models.CharField(max_length=20, choices=InstitutionType.choices, default=InstitutionType.OTHER)
    ownership = models.CharField(max_length=255, blank=True, null=True)
    funding_source = models.CharField(max_length=255, blank=True, null=True)

    # Metadata
    established_year = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    extra_info = models.JSONField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['county']),
            models.Index(fields=['sub_county']),
            models.Index(fields=['ward']),
            models.Index(fields=['village']),
            models.Index(fields=['code']),
        ]
        ordering = ['name']
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")

    def __str__(self):
        return self.name


# =========================
# School Account Model
# =========================
class SchoolAccount(models.Model):
    BANK = 'bank'
    MOBILE_MONEY = 'mobile_money'
    PAYMENT_TYPES = [
        (BANK, _('Bank Account')),
        (MOBILE_MONEY, _('Mobile Money')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='accounts')
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    mpesa_till_number = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('institution', 'account_number')]
        ordering = ['institution', 'account_name']
        verbose_name = _("School Account")
        verbose_name_plural = _("School Accounts")

    def __str__(self):
        return f"{self.institution.name} - {self.account_name} ({self.get_payment_type_display()})"


# =========================
# Pending School Registration
# =========================
class SchoolRegistrationRequest(models.Model):
    """
    Captures school registration submissions before verification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school_name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    country = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100, blank=True, null=True)
    ward = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    institution_type = models.CharField(max_length=50, choices=InstitutionType.choices, default=InstitutionType.OTHER)
    school_type = models.CharField(max_length=50, choices=SchoolType.choices, default=SchoolType.OTHER)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(blank=True, null=True)
    admin_created = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = _("School Registration Request")
        verbose_name_plural = _("School Registration Requests")

    def __str__(self):
        return f"{self.school_name} ({self.code})"
