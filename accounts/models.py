from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class Institution(models.Model):
    """
    Basic institution reference to enforce FK integrity.
    Branding, M-Pesa configs, themes, etc., are handled in the institutions app.
    """
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', CustomUser.Role.SUPER_ADMIN)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        ADMIN = "ADMIN", "School Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"
        LIBRARIAN = "LIBRARIAN", "Librarian"
        STORE_KEEPER = "STORE_KEEPER", "Store Keeper"
        BURSAR = "BURSAR", "Bursar"
        HOSTEL_MANAGER = "HOSTEL_MANAGER", "Hostel Manager"
        FINANCE = "FINANCE", "Finance Officer"
        SUPPORT_STAFF = "SUPPORT_STAFF", "Support Staff"
        PUBLIC_LEARNER = "PUBLIC_LEARNER", "Public Learner"
        PUBLIC_TEACHER = "PUBLIC_TEACHER", "Public Teacher"
        GOV_USER = "GOV_USER", "Government User"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)

    role = models.CharField(max_length=30, choices=Role.choices)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Only institutional users have this set. Public and GOV users have it null."
    )

    #  Added fields
    profile_picture = models.ImageField(upload_to='user_avatars/', null=True, blank=True)
    reset_token = models.CharField(max_length=64, null=True, blank=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    # Optional audit/session metadata
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_user_agent = models.TextField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.email} ({self.role})"

    # Role-based helpers
    @property
    def is_school_admin(self):
        return self.role == self.Role.ADMIN and self.institution is not None

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def is_public(self):
        return self.role in {self.Role.PUBLIC_LEARNER, self.Role.PUBLIC_TEACHER}

    @property
    def is_institution_user(self):
        return self.institution is not None and not self.is_public

    @property
    def is_government_user(self):
        return self.role == self.Role.GOV_USER
