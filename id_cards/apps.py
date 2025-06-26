# id_cards/apps.py

from django.apps import AppConfig

class IDCardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'id_cards'
    verbose_name = 'ID Card Management'

    def ready(self):
        import id_cards.signals  # ensures signals are registered on app load
