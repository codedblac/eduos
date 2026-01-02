from django.db import models
from django.contrib.auth.models import Group, Permission
from institutions.models import Institution
from django.utils.text import slugify


# ---------------------------------------------------
# 1. SystemModule: auto-generated from installed apps
# ---------------------------------------------------
class SystemModule(models.Model):
    """
    Represents a system module (exams, library, HRM, etc.).
    Each module automatically gets a matching group for permission assignment.
    """
    name = models.CharField(max_length=100, unique=True)
    app_label = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=True)  # default module for plans

    linked_group = models.OneToOneField(
        Group, on_delete=models.SET_NULL, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        # Auto-create linked group if missing
        if not self.linked_group:
            group_name = f"{slugify(self.name)}-module-group"
            group, created = Group.objects.get_or_create(name=group_name)
            self.linked_group = group

        super().save(*args, **kwargs)

        # Assign all app-level permissions to the linked group
        perms = Permission.objects.filter(content_type__app_label=self.app_label)
        if self.linked_group:
            self.linked_group.permissions.set(perms)

    def __str__(self):
        return self.name


# ---------------------------------------------------
# 2. Plan: Dynamic subscription plans
# ---------------------------------------------------
class Plan(models.Model):
    """
    Represents a subscription plan.
    - Super admin can create new plans dynamically in admin.
    - Modules linked to plan are automatically assigned on onboarding.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    modules = models.ManyToManyField(SystemModule, blank=True, related_name="plans")
    is_custom = models.BooleanField(default=False)  # If True, admin chooses modules manually

    def __str__(self):
        return self.name


# ---------------------------------------------------
# 3. ModulePermission: Extra custom permissions
# ---------------------------------------------------
class ModulePermission(models.Model):
    """
    Represents extra custom permissions per module.
    """
    module = models.ForeignKey(
        SystemModule, on_delete=models.CASCADE, related_name='custom_permissions'
    )
    name = models.CharField(max_length=150)
    codename = models.CharField(max_length=150)

    class Meta:
        unique_together = ('module', 'codename')

    def __str__(self):
        return f"{self.module.name} - {self.name}"


# ---------------------------------------------------
# 4. SchoolModule: Which modules a school can use
# ---------------------------------------------------
class SchoolModule(models.Model):
    """
    Tracks modules that each institution has access to.
    - On onboarding, modules are assigned based on selected Plan.
    - Institution Admin can add custom modules manually.
    """
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="allowed_modules"
    )
    module = models.ForeignKey(SystemModule, on_delete=models.CASCADE)
    custom = models.BooleanField(default=False)  # Marks if added by admin

    class Meta:
        unique_together = ("institution", "module")

    def __str__(self):
        return f"{self.institution.name} - {self.module.name}"

    # ---------------------------
    # Assign modules from plan
    # ---------------------------
    @classmethod
    def assign_plan_modules(cls, institution, plan: Plan):
        """
        Assign all modules from the selected plan to the institution.
        """
        for module in plan.modules.all():
            cls.objects.get_or_create(institution=institution, module=module)

    # ---------------------------
    # Assign a custom module
    # ---------------------------
    @classmethod
    def assign_custom_module(cls, institution, module):
        """
        Adds a custom module to the institution if not already assigned.
        """
        obj, created = cls.objects.get_or_create(institution=institution, module=module)
        if created:
            obj.custom = True
            obj.save()
        return obj

    # ---------------------------
    # Get all modules available to institution
    # ---------------------------
    @staticmethod
    def get_institution_modules(institution):
        """
        Returns all modules available to a given institution.
        """
        return SystemModule.objects.filter(
            id__in=institution.allowed_modules.values_list('module_id', flat=True)
        )
