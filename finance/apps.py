from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'
    verbose_name = 'Finance & Budgeting Module'

    def ready(self):
        try:
            import finance.signals  # Ensure signal handlers are registered
        except Exception as e:
            logger.error(f"Failed to import finance signals: {e}")
