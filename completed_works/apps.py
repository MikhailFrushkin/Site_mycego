from django.apps import AppConfig


class CompletedWorksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'completed_works'

    def ready(self):
        from completed_works.scheduler import scheduler
        scheduler.start()
