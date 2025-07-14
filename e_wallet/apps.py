from django.apps import AppConfig


class EWalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'e_wallet'
    verbose_name = "EduOS E-Wallet System"

    def ready(self):
        # Import signals to register them with Django when the app is ready
        from . import signals
