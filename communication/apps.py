from django.apps import AppConfig


class CommunicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'communication'
    verbose_name = "Communication & Announcements"

    def ready(self):
        import communication.signals  # noqa
