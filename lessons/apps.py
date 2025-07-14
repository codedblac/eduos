from django.apps import AppConfig


class LessonsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lessons'
    verbose_name = 'Lesson Planning & Delivery'

    def ready(self):
        import lessons.signals  # Ensures signal handlers are registered at startup
