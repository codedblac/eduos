from django.apps import AppConfig

class ELearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'e_learning'
    verbose_name = "E-Learning Platform"

    def ready(self):
        import e_learning.signals  # Ensures signals are registered on app load
