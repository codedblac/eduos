from django.apps import AppConfig


class FrontOfficeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'front_office'

def ready(self):
    import front_office.signals
