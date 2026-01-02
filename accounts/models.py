from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from institutions.models import Institution
from modules.models import SystemModule, ModulePermission, SchoolModule
from django.contrib.auth.models import Permission



# ---------------------
# User Manager
# ---------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
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
        STAFF = "STAFF", "General Staff"
        PUBLIC_LEARNER = "PUBLIC_LEARNER", "Public Learner"
        PUBLIC_TEACHER = "PUBLIC_TEACHER", "Public Teacher"
        GOV_USER = "GOV_USER", "Government User"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    primary_role = models.CharField(max_length=30, choices=Role.choices, default=Role.STAFF)

    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)

    profile_picture = models.ImageField(upload_to='user_avatars/', null=True, blank=True)
    reset_token = models.CharField(max_length=64, null=True, blank=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_user_agent = models.TextField(null=True, blank=True)

    # ---------------------
    # Modules & Permissions
    # ---------------------
    modules = models.ManyToManyField(SystemModule, blank=True, related_name="users")
    module_permissions = models.ManyToManyField(ModulePermission, blank=True, related_name="users")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.primary_role})"

    # ---------------------
    # Role Properties
    # ---------------------
    @property
    def is_super_admin(self):
        return self.primary_role == self.Role.SUPER_ADMIN

    @property
    def is_institution_admin(self):
        return self.primary_role == self.Role.INSTITUTION_ADMIN

    # ---------------------
    # Module Access Properties
    # ---------------------
    @property
    def available_modules(self):
        """
        Returns list of module names available to the user.
        Super Admin gets all modules automatically.
        """
        if self.is_super_admin:
            return list(SystemModule.objects.values_list('name', flat=True))
        return [module.name for module in self.modules.all()]

    @property
    def all_permissions(self):
        """
        Returns all permission codenames the user has:
        - Via module linked groups
        - Via custom ModulePermission
        - Super Admin gets all permissions automatically
        """
        perms = set()

        if self.is_super_admin:
            perms.update(
                Permission.objects.all().values_list('codename', flat=True)
            )
            return list(perms)

        for module in self.modules.all():
            # Permissions via module's linked group
            if module.linked_group:
                perms.update(module.linked_group.permissions.values_list('codename', flat=True))
            # Extra module-specific permissions
            perms.update(module.custom_permissions.values_list('codename', flat=True))

        # Direct user-assigned module permissions
        perms.update(self.module_permissions.values_list('codename', flat=True))
        return list(perms)
