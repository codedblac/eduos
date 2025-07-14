# timetable/apps.py

from django.apps import AppConfig


class TimetableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timetable'
    verbose_name = "AI Timetable Management"

    def ready(self):
        # Register signals
        import timetable.signals
