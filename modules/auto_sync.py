from django.conf import settings
from django.apps import apps
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

    # Core apps that are NOT modules
    # "accounts",
    # "institutions",
    # "modules",
]

def sync_modules():
    """
    Auto-create SystemModules for all valid local apps in INSTALLED_APPS.
    Skips excluded apps.
    """
    installed_apps = settings.INSTALLED_APPS

    for app in installed_apps:
        # Skip excluded apps
        if any(app.startswith(prefix) for prefix in EXCLUDED_APPS):
            continue

        try:
            # Get the AppConfig for the app
            app_config = apps.get_app_config(app.split('.')[-1])
        except LookupError:
            continue  # Skip if app config cannot be found

        # Create SystemModule if not already present
        module, created = SystemModule.objects.get_or_create(
            app_label=app_config.label,
            defaults={
                "name": app_config.verbose_name or app_config.label.replace("_", " ").title(),
                "description": f"Auto-generated module for {app_config.label}",
                "is_default": True,
            }
        )

        if not created:
            # Optionally, update the name/description if needed
            module.name = app_config.verbose_name or module.name
            module.description = module.description or f"Auto-generated module for {app_config.label}"
            module.save()
