from django.apps import AppConfig


class GuardiansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'guardians'
    verbose_name = 'Guardian Management'

    def ready(self):
        import guardians.signals  # Ensures signals are registered
