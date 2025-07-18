# assessments/apps.py

from django.apps import AppConfig


class AssessmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assessments'
    verbose_name = "Assessments and Exams"

    def ready(self):
        import assessments.signals  
