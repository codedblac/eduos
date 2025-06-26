# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class Institution(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='institution_logos/', null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    # Branding
    primary_color = models.CharField(max_length=20, default="#0047AB")  # hex code
    secondary_color = models.CharField(max_length=20, default="#FFFFFF")
    theme_mode = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')

    # M-Pesa Integration
    mpesa_paybill = models.CharField(max_length=20, blank=True, null=True)
    mpesa_shortcode = models.CharField(max_length=20, blank=True, null=True)
    mpesa_account_name = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
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
        PARENT = "PARENT", "Parent"
        PUBLIC_LEARNER = "PUBLIC_LEARNER", "Public Learner"
        PUBLIC_TEACHER = "PUBLIC_TEACHER", "Public Teacher"
        LIBRARIAN = "LIBRARIAN", "Librarian"
        STORE_KEEPER = "STORE_KEEPER", "Store Keeper"
        BURSAR = "BURSAR", "Bursar"
        HOSTEL_MANAGER = "HOSTEL_MANAGER", "Hostel Manager"
        FINANCE = "FINANCE", "Finance Officer"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)

    role = models.CharField(max_length=30, choices=Role.choices)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    def __str__(self):
        return self.email

    @property
    def is_school_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def is_public(self):
        return self.role in [self.Role.PUBLIC_LEARNER, self.Role.PUBLIC_TEACHER]
