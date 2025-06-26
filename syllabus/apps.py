from django.apps import AppConfig


class SyllabusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'syllabus'
    verbose_name = "Curriculum & Syllabus Management"

    def ready(self):
        import syllabus.signals  # Ensures signal handlers are registered
