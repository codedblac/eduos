# accounts/utils.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import CustomUser, Institution


# ---------------------------
#  Email utilities
# ---------------------------

def normalize_email(email: str) -> str:
    """Normalize email by lowering case and stripping whitespace."""
    return email.strip().lower()


def validate_school_email_domain(email: str, domain: str):
    """Ensure email matches institution’s domain."""
    if not email.endswith(f"@{domain}"):
        raise ValidationError(_("Email must end with @%(domain)s"), params={'domain': domain})


# ---------------------------
#  Role & access utilities
# ---------------------------

def is_role(user: CustomUser, role_name: str) -> bool:
    """Check if user has a role by name."""
    return user.primary_role == role_name


def is_institution_member(user: CustomUser, institution: Institution) -> bool:
    """Check if user belongs to the given institution."""
    return user.institution == institution


def can_manage_user(manager: CustomUser, target: CustomUser) -> bool:
    """
    Allow SUPER_ADMIN to manage everyone.
    Allow INSTITUTION_ADMIN to manage users within the same institution.
    """
    if manager.primary_role == CustomUser.Role.SUPER_ADMIN:
        return True
    return (
        manager.primary_role == CustomUser.Role.INSTITUTION_ADMIN and
        manager.institution == target.institution
    )


# ---------------------------
#  Account switching (placeholder)
# ---------------------------

def is_switchable_account(requesting_user: CustomUser, target_user: CustomUser) -> bool:
    """
    Determine if a user can switch accounts.
    (Placeholder: recommended to replace with real linked account logic)
    """
    if requesting_user.primary_role == "PARENT":
        return True
    if requesting_user.primary_role == CustomUser.Role.INSTITUTION_ADMIN:
        return requesting_user.institution == target_user.institution
    return False


# ---------------------------
#  Institution helpers
# ---------------------------

def get_institution_from_email(email: str) -> Institution | None:
    """
    For future use: match email domain to an institution.
    Assumes institution.location stores something similar.
    """
    domain = email.split('@')[-1].lower()
    return Institution.objects.filter(location__icontains=domain).first()


# ---------------------------
#  Timestamp utility
# ---------------------------

def now():
    """Return timezone-aware current time."""
    return timezone.now()


# ---------------------------
#  Phone number handling
# ---------------------------

def normalize_phone_number(phone: str) -> str:
    """Normalize Kenyan phone number to international format."""
    if not phone:
        return ""
    phone = phone.strip().replace(" ", "")
    if phone.startswith("0"):
        return "+254" + phone[1:]
    if phone.startswith("254"):
        return "+" + phone
    if phone.startswith("+254"):
        return phone
    raise ValidationError(_("Invalid Kenyan phone number format."))


# ---------------------------
#  Role metadata (UI support)
# ---------------------------

ROLE_MAP = {
    "SUPER_ADMIN": {
        "label": "Super Admin",
        "can_create_users": True,
        "can_manage_all": True,
        "description": "Full platform access.",
        "visible_in_dropdown": True,
    },
    "INSTITUTION_ADMIN": {
        "label": "Institution Admin",
        "can_create_users": True,
        "can_manage_school": True,
        "description": "Manages school operations and users.",
        "visible_in_dropdown": True,
    },
    "TEACHER": {"label": "Teacher", "visible_in_dropdown": True},
    "STUDENT": {"label": "Student", "visible_in_dropdown": True},
    "LIBRARIAN": {"label": "Librarian", "visible_in_dropdown": True},
    "STORE_KEEPER": {"label": "Store Keeper", "visible_in_dropdown": True},
    "BURSAR": {"label": "Bursar", "visible_in_dropdown": True},
    "HOSTEL_MANAGER": {"label": "Hostel Manager", "visible_in_dropdown": True},
    "FINANCE": {"label": "Finance Officer", "visible_in_dropdown": True},
    "PUBLIC_LEARNER": {"label": "Public Learner", "visible_in_dropdown": True},
    "PUBLIC_TEACHER": {"label": "Public Teacher", "visible_in_dropdown": True},
    "GOV_USER": {"label": "Government User", "visible_in_dropdown": True},
}


def get_role_label(role_key: str) -> str:
    """Return human-readable name for role."""
    return ROLE_MAP.get(role_key, {}).get("label", role_key)


def get_role_details(role_key: str) -> dict:
    """Return metadata (label, description, abilities) for a role key."""
    return ROLE_MAP.get(role_key, {"label": role_key, "description": "Unknown role"})
