from django.apps import AppConfig


class AccessControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'access_control'
    verbose_name = "Access Control & Permissions"

    def ready(self):
        import access_control.signals  # Register signal handlers
