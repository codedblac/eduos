# accounts/utils.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import CustomUser, Institution

# ===============================
# 🔒 Email utilities
# ===============================

def normalize_email(email: str) -> str:
    """Normalize email by lowering case and stripping whitespace."""
    return email.strip().lower()


def validate_school_email_domain(email: str, domain: str):
    """
    Validate that an email belongs to a specific school's domain.
    Useful for enforcing institutional email rules.
    """
    if not email.endswith(f"@{domain}"):
        raise ValidationError(_("Email must end with @%(domain)s"), params={'domain': domain})


# ===============================
# 👤 Role & access utilities
# ===============================

def is_role(user: CustomUser, role: str) -> bool:
    """Check if a user has a specific role."""
    return user.role == role


def is_institution_member(user: CustomUser, institution: Institution) -> bool:
    """Check if user belongs to the given institution."""
    return user.institution == institution


def can_manage_user(manager: CustomUser, target: CustomUser) -> bool:
    """Logic to determine if manager can manage (view/update/delete) a target user."""
    if manager.role == CustomUser.Role.SUPER_ADMIN:
        return True
    return manager.institution == target.institution and manager.role in [
        CustomUser.Role.ADMIN,
    ]


# ===============================
# 🔄 Account switching logic
# ===============================

def is_switchable_account(requesting_user: CustomUser, target_user: CustomUser) -> bool:
    """
    Determine if a user is allowed to switch into another account (e.g., child).
    This is a placeholder — real logic should use linked accounts.
    """
    if requesting_user.role == CustomUser.Role.PARENT:
        return True  # Placeholder logic
    if requesting_user.role == CustomUser.Role.ADMIN and requesting_user.institution == target_user.institution:
        return True
    return False


# ===============================
# 🏫 Institution helpers
# ===============================

def get_institution_from_email(email: str) -> Institution | None:
    """
    Match domain to institution — useful if using email like user@schoolname.eduos.ke.
    """
    domain = email.split('@')[-1].lower()
    return Institution.objects.filter(location__icontains=domain).first()


# ===============================
# 📅 Timestamp utility
# ===============================

def now():
    """Return timezone-aware current time."""
    return timezone.now()


# ===============================
# 📞 Phone number utilities
# ===============================

def normalize_phone_number(phone: str) -> str:
    """
    Normalize Kenyan phone numbers to international format.
    E.g. 0712345678 → +254712345678
    """
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


# ===============================
# 🔄 Role label + details
# ===============================

def get_role_label(role_key: str) -> str:
    """Return human-readable label for a role key."""
    for r in CustomUser.Role.choices:
        if r[0] == role_key:
            return r[1]
    return role_key


ROLE_MAP = {
    "SUPER_ADMIN": {
        "label": "Super Admin",
        "can_create_users": True,
        "can_manage_all": True,
        "description": "Top-level platform admin with access to all schools and modules.",
        "visible_in_dropdown": True,
    },
    "ADMIN": {
        "label": "School Admin",
        "can_create_users": True,
        "can_manage_school": True,
        "description": "Manages school operations, staff, and roles.",
        "visible_in_dropdown": True,
    },
    "TEACHER": {
        "label": "Teacher",
        "can_access_class": True,
        "can_upload_materials": True,
        "description": "Manages classes, assessments, and content.",
        "visible_in_dropdown": True,
    },
    "STUDENT": {
        "label": "Student",
        "can_view_materials": True,
        "can_take_exams": True,
        "description": "Learner enrolled in a school or public stream.",
        "visible_in_dropdown": True,
    },
    "PARENT": {
        "label": "Parent",
        "can_view_fees": True,
        "can_view_performance": True,
        "description": "Views student reports, attendance, and makes fee payments.",
        "visible_in_dropdown": False,
    },
    "PUBLIC_LEARNER": {
        "label": "Public Learner",
        "can_use_public_content": True,
        "description": "Independent learner accessing EduOS Learning.",
        "visible_in_dropdown": True,
    },
    "PUBLIC_TEACHER": {
        "label": "Public Tutor",
        "can_upload_public_content": True,
        "description": "Independent tutor publishing or using EduOS content.",
        "visible_in_dropdown": True,
    },
    "LIBRARIAN": {
        "label": "Librarian",
        "description": "Manages the institution's library system.",
        "visible_in_dropdown": True,
    },
    "STORE_KEEPER": {
        "label": "Store Keeper",
        "description": "Manages inventory and procurement.",
        "visible_in_dropdown": True,
    },
    "BURSAR": {
        "label": "Bursar",
        "description": "Handles fee tracking, invoices, and finance reports.",
        "visible_in_dropdown": True,
    },
    "HOSTEL_MANAGER": {
        "label": "Hostel Manager",
        "description": "Manages student accommodation.",
        "visible_in_dropdown": True,
    },
    "FINANCE": {
        "label": "Finance Officer",
        "description": "Oversees institutional-level financials.",
        "visible_in_dropdown": True,
    },
}


def get_role_details(role_key: str) -> dict:
    """Return metadata (label, description, abilities) for a role key."""
    return ROLE_MAP.get(role_key, {"label": role_key, "description": "Unknown role"})
