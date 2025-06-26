from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class FileManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'file_manager'
    verbose_name = "EduOS File Manager"

    def ready(self):
        try:
            import file_manager.signals  # Ensure signals are registered
            logger.debug("file_manager.signals successfully loaded.")
        except ImportError as e:
            logger.error(f"Failed to import file_manager.signals: {e}")
