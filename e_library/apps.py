from django.apps import AppConfig


class ELibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'e_library'
    verbose_name = "e-Library"

    def ready(self):
        import e_library.signals  
