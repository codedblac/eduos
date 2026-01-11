from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Permission
from .models import SystemModule

EXCLUDED_APPS = [
    "django.contrib.",
    "rest_framework",
    "corsheaders",
    "drf_yasg",
    "django_filters",
    "django_celery",
    "channels",
    "import_export",
    "taggit",
    "auditlog",
    "django_daraja",

    # core system apps that are NOT modules
    # "accounts",
    # "institutions",
    # "modules",
    "landing",
]

def is_valid_module(app_label: str) -> bool:
    """Checks whether an app should be considered a real module."""
    if any(app_label.startswith(prefix) for prefix in EXCLUDED_APPS):
        return False
    return True

# -----------------------------------------------------
# 1. Auto-create modules after migrations
# -----------------------------------------------------
@receiver(post_migrate)
def create_modules_after_migrate(sender, **kwargs):
    """
    After migrations:
    - Detect new local apps
    - Create missing SystemModules
    - Assign permissions to module groups
    """
    for app_config in apps.get_app_configs():
        label = app_config.label

        if not is_valid_module(label):
            continue

        module, created = SystemModule.objects.get_or_create(
            app_label=label,
            defaults={
                "name": app_config.verbose_name or label.replace("_", " ").title(),
                "description": f"Auto-generated module for {label}",
                "is_default": True,  # mark new modules as default
            }
        )

        # Sync permissions for existing or new modules
        perms = Permission.objects.filter(content_type__app_label=label)
        if module.linked_group:
            module.linked_group.permissions.set(perms)

# -----------------------------------------------------
# 2. Sync module group permissions on save
# -----------------------------------------------------
@receiver(post_save, sender=SystemModule)
def sync_permissions_on_module_save(sender, instance, **kwargs):
    """
    Whenever a SystemModule is saved:
    - Ensure its linked group has all current app permissions
    """
    perms = Permission.objects.filter(content_type__app_label=instance.app_label)
    if instance.linked_group:
        instance.linked_group.permissions.set(perms)
