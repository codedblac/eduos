# accounts/utils.py

import random
import string
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


def generate_unique_school_code(name):
    """
    Generate a unique institution code from its name.
    """
    base_slug = slugify(name)
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_slug}-{suffix}"


def generate_username_from_email(email):
    """
    Generate a simple username from an email address.
    Ensures uniqueness by adding random digits.
    """
    return email.split('@')[0] + ''.join(random.choices(string.digits, k=4))


def get_tokens_for_user(user):
    """
    Generates JWT tokens (refresh + access) for a given user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def validate_role_for_school_user(role):
    """
    Validates that the role is allowed during institution-based user creation.
    Disallows public or special roles during institution registration.
    """
    allowed_roles = ['admin', 'teacher', 'student', 'parent']
    if role not in allowed_roles:
        raise ValidationError(_(f"{role} is not allowed during school-based user creation."))


def get_role_display(role):
    """
    Returns a human-readable display name for a given role.
    Useful in serializers, templates, or frontend display.
    """
    roles_map = {
        'admin': 'Admin',
        'teacher': 'Teacher',
        'student': 'Student',
        'parent': 'Parent',
        'public_learner': 'Public Learner',
        'public_teacher': 'Public Teacher / Contributor',
        'super_admin': 'School Principal',
        'librarian': 'Librarian',
        'storekeeper': 'Storekeeper',
        'bursar': 'Bursar',
        'hostel_manager': 'Hostel Manager',
        'finance_officer': 'Finance Officer',
    }
    return roles_map.get(role, 'Unknown Role')
