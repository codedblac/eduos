from django.apps import AppConfig


class FeeManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fee_management'
    verbose_name = "Fee Management"

    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures all payment, invoice, and refund logic is active.
        """
        import fee_management.signals  # noqa
