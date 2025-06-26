# co_curricular/apps.py

from django.apps import AppConfig


class CoCurricularConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'co_curricular'
    verbose_name = "Co-Curricular & Talent Management"

    def ready(self):
        import co_curricular.signals  # Ensures signals are registered on app load
