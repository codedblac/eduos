from django.apps import AppConfig

class DisciplineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'discipline'

    def ready(self):
        import discipline.signals
