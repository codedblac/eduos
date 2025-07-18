from django.apps import AppConfig


class ExamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exams'
    verbose_name = 'Examinations & Results'

    def ready(self):
        import exams.signals  # noqa
