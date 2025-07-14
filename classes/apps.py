from django.apps import AppConfig


class ClassesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classes'
    verbose_name = 'Class Levels & Streams'

    def ready(self):
        # Import signals to ensure they are registered when the app is ready
        import classes.signals
