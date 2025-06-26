# admissions/apps.py

from django.apps import AppConfig

class AdmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admissions'
    verbose_name = "Admissions and Applicant Management"

    def ready(self):
        import admissions.signals  # Ensures signals are connected when the app is ready
