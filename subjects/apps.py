from django.apps import AppConfig


class SubjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subjects'
    verbose_name = "Subjects and Curriculum Management"

    def ready(self):
        import subjects.signals  # Ensures signal handlers are registered on app load
