# institutions/models.py
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text=_("Unique school code"))
    registration_number = models.CharField(max_length=100, blank=True, null=True, help_text=_("Government registration number"))

    # Location hierarchy for detailed geolocation / govt analysis
    country = models.CharField(max_length=100, default='Kenya')
    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    village = models.CharField(max_length=100, blank=True, null=True)

    # Contacts
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Branding & theming
    logo = models.ImageField(upload_to='institution_logos/', blank=True, null=True)
    theme_color = models.CharField(max_length=7, default='#003366', help_text=_("Primary hex color code"))

    # School type, ownership, funding
    SCHOOL_TYPES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('community', 'Community'),
        ('other', 'Other'),
    ]
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPES)

    ownership = models.CharField(max_length=255, blank=True, null=True)
    funding_source = models.CharField(max_length=255, blank=True, null=True, help_text=_("Main source of funding (e.g., govt, donors, fees)"))

    # Date fields
    established_year = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # For extensibility
    extra_info = models.JSONField(blank=True, null=True, help_text=_("Additional metadata or info in JSON"))

    def __str__(self):
        return self.name


class SchoolAccount(models.Model):
    BANK = 'bank'
    MOBILE_MONEY = 'mobile_money'
    PAYMENT_TYPES = [
        (BANK, 'Bank Account'),
        (MOBILE_MONEY, 'Mobile Money'),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='accounts')
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    branch = models.CharField(max_length=255, blank=True, null=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    mpesa_till_number = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('institution', 'account_number')]

    def __str__(self):
        return f"{self.institution.name} - {self.account_name} ({self.get_payment_type_display()})"
