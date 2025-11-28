from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from institutions.models import Institution




# ---------------------
# Module Model (Dynamic Access Control)
# ---------------------
class SystemModule(models.Model):
    """
    Represents dashboards/modules within the institution system.
    Example: Finance, Library, Hostel, Academics...
    Allows admin to create custom modules dynamically.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=True)  # Default system modules

    def __str__(self):
        return self.name


# ---------------------
# User Manager
# ---------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        # Ensure primary_role is a string if passed as Role enum
        if 'primary_role' in extra_fields and isinstance(extra_fields['primary_role'], models.TextChoices):
            extra_fields['primary_role'] = extra_fields['primary_role'].value
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Force superuser to always be SUPER_ADMIN
        """
        extra_fields['primary_role'] = CustomUser.Role.SUPER_ADMIN
        extra_fields['is_superuser'] = True
        extra_fields['is_staff'] = True
        return self.create_user(email, password, **extra_fields)


# ---------------------
# User Model
# ---------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        INSTITUTION_ADMIN = "INSTITUTION_ADMIN", "Institution Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"
        STAFF = "STAFF", "General Staff"  # Staff with multiple modules
        PUBLIC_LEARNER = "PUBLIC_LEARNER", "Public Learner"
        PUBLIC_TEACHER = "PUBLIC_TEACHER", "Public Teacher"
        GOV_USER = "GOV_USER", "Government User"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)

    # PRIMARY ROLE (Main dashboard category)
    primary_role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.STAFF  # Default to STAFF if not provided
    )

    # MODULE ACCESS (Multiple modules)
    modules = models.ManyToManyField(SystemModule, blank=True, related_name="users")

    institution = models.ForeignKey(
        Institution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    profile_picture = models.ImageField(upload_to='user_avatars/', null=True, blank=True)
    reset_token = models.CharField(max_length=64, null=True, blank=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_user_agent = models.TextField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.primary_role})"

    # -----------------
    # Helper properties
    # -----------------
    @property
    def is_super_admin(self):
        return self.primary_role == self.Role.SUPER_ADMIN

    @property
    def is_institution_admin(self):
        return self.primary_role == self.Role.INSTITUTION_ADMIN

    @property
    def is_public(self):
        return self.primary_role in {self.Role.PUBLIC_LEARNER, self.Role.PUBLIC_TEACHER}

    @property
    def available_modules(self):
        return [module.name for module in self.modules.all()]
